from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum, Count
from django.conf import settings
from .models import Booking, Review, ContactMessage


def _pack_image_url(pack_name):
    """Devolve o caminho estático da imagem do pack conforme o nome (catálogo)."""
    if not pack_name:
        return None
    name = (pack_name or '').lower()
    if 'zforce' in name:
        return 'images/card2.png'
    if 'cf moto' in name or 'cf buggy' in name or 'moto' in name or 'buggy' in name:
        return 'images/card.png'
    return 'images/card.png'  # placeholder genérico


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('pack_thumb', 'id', 'user_link', 'pack_name', 'pack_price', 'booking_date', 'status_badge', 'created_at', 'payment_info')
    list_filter = ('status', 'created_at', 'booking_date')
    search_fields = ('user__email', 'user__username', 'pack_name', 'stripe_payment_intent_id')
    readonly_fields = ('created_at', 'payment_info', 'user_info')
    list_per_page = 50
    date_hierarchy = 'created_at'
    actions = ['approve_bookings', 'cancel_bookings', 'mark_completed']
    
    fieldsets = (
        ('Informações do Cliente', {
            'fields': ('user_info', 'user')
        }),
        ('Detalhes da Reserva', {
            'fields': ('pack_name', 'pack_price', 'booking_date', 'status', 'addons')
        }),
        ('Pagamento', {
            'fields': ('payment_info', 'stripe_payment_intent_id')
        }),
        ('Sistema', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'Cliente'
    user_link.admin_order_field = 'user__email'

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',    # amarelo
            'confirmed': '#10b981',   # verde
            'cancelled': '#ef4444',   # vermelho
            'completed': '#3b82f6',   # azul
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def pack_thumb(self, obj):
        from django.templatetags.static import static
        path = _pack_image_url(obj.pack_name)
        url = static(path) if path else ''
        if url:
            return format_html(
                '<img src="{}" alt="{}" style="width: 48px; height: 48px; object-fit: cover; border-radius: 6px; border: 1px solid #e5e7eb;">',
                url, (obj.pack_name or '')[:30]
            )
        return format_html('<span style="color: #9ca3af;">—</span>')
    pack_thumb.short_description = 'Produto'

    def payment_info(self, obj):
        if obj.stripe_payment_intent_id:
            return format_html(
                '<strong>Stripe:</strong> {}<br><small style="color: #10b981;">✓ Pagamento confirmado</small>',
                obj.stripe_payment_intent_id[:20] + '...'
            )
        return format_html('<span style="color: #f59e0b;">Aguardando pagamento</span>')
    payment_info.short_description = 'Informações de Pagamento'

    def user_info(self, obj):
        return format_html(
            '<strong>Nome:</strong> {}<br>'
            '<strong>Email:</strong> {}<br>'
            '<strong>Membro desde:</strong> {}',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email,
            obj.user.date_joined.strftime('%d/%m/%Y')
        )
    user_info.short_description = 'Dados do Cliente'

    def approve_bookings(self, request, queryset):
        count = queryset.update(status='confirmed')
        self.message_user(request, f'{count} reserva(s) aprovada(s) com sucesso.')
    approve_bookings.short_description = '✅ Aprovar reservas selecionadas'

    def cancel_bookings(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f'{count} reserva(s) cancelada(s).')
    cancel_bookings.short_description = '❌ Cancelar reservas selecionadas'

    def mark_completed(self, request, queryset):
        count = queryset.update(status='completed')
        self.message_user(request, f'{count} reserva(s) marcada(s) como concluída(s).')
    mark_completed.short_description = '✓ Marcar como concluídas'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Estatísticas gerais
        total_bookings = Booking.objects.count()
        total_revenue = Booking.objects.aggregate(Sum('pack_price'))['pack_price__sum'] or 0
        
        # Reservas por status
        stats_by_status = Booking.objects.values('status').annotate(
            count=Count('id'),
            revenue=Sum('pack_price')
        )
        
        # Reservas hoje
        today = timezone.now().date()
        bookings_today = Booking.objects.filter(created_at__date=today).count()
        revenue_today = Booking.objects.filter(created_at__date=today).aggregate(
            Sum('pack_price')
        )['pack_price__sum'] or 0
        
        # Reservas este mês
        month_start = timezone.now().replace(day=1).date()
        bookings_this_month = Booking.objects.filter(created_at__date__gte=month_start).count()
        revenue_this_month = Booking.objects.filter(created_at__date__gte=month_start).aggregate(
            Sum('pack_price')
        )['pack_price__sum'] or 0

        # Reservas confirmadas
        confirmed = Booking.objects.filter(status='confirmed')
        confirmed_count = confirmed.count()
        confirmed_revenue = confirmed.aggregate(Sum('pack_price'))['pack_price__sum'] or 0

        extra_context['stats'] = {
            'total_bookings': total_bookings,
            'total_revenue': float(total_revenue),
            'confirmed_count': confirmed_count,
            'confirmed_revenue': float(confirmed_revenue),
            'bookings_today': bookings_today,
            'revenue_today': float(revenue_today),
            'bookings_this_month': bookings_this_month,
            'revenue_this_month': float(revenue_this_month),
            'by_status': list(stats_by_status),
        }
        
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'pack_name', 'rating_stars', 'is_approved_badge', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at', 'pack_name')
    search_fields = ('user__email', 'user__username', 'pack_name', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    actions = ['approve_reviews', 'disapprove_reviews']
    
    fieldsets = (
        ('Avaliação', {
            'fields': ('user', 'booking', 'pack_name', 'rating', 'comment', 'is_approved')
        }),
        ('Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'Cliente'
    user_link.admin_order_field = 'user__email'

    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span style="font-size: 18px;">{}</span> <span style="color: #f59e0b;">({}/5)</span>', stars, obj.rating)
    rating_stars.short_description = 'Avaliação'
    rating_stars.admin_order_field = 'rating'

    def is_approved_badge(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ Aprovada</span>'
            )
        return format_html(
            '<span style="background-color: #f59e0b; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">⏳ Pendente</span>'
        )
    is_approved_badge.short_description = 'Status'
    is_approved_badge.admin_order_field = 'is_approved'

    def approve_reviews(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f'{count} avaliação(ões) aprovada(s) com sucesso.')
    approve_reviews.short_description = '✅ Aprovar avaliações selecionadas'

    def disapprove_reviews(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} avaliação(ões) reprovada(s).')
    disapprove_reviews.short_description = '❌ Reprovar avaliações selecionadas'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    list_per_page = 30
    date_hierarchy = 'created_at'
