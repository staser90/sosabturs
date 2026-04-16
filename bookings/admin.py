import json

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum, Count
from .models import Booking, Review, ContactMessage
from .utils import send_booking_update_email

# Mesmas imagens que em templates/catalogo.html (data-image / hero do pack)
_PACK_GALLERY = {
    'zforce_4': 'images/galeria/Zforce4100.JPG',
    'zforce': 'images/galeria/moto2.JPG',
    'cf_moto': 'images/galeria/moto2.JPG',
    'cf_buggy': 'images/galeria/moto3.JPG',
}


def _pack_image_url(pack_name, addons_json=None):
    """Caminho estático da miniatura conforme o pack (catálogo SO SAB)."""
    name = (pack_name or '').strip()
    if not name and addons_json:
        try:
            parsed = json.loads(addons_json)
            items = parsed.get('items') if isinstance(parsed, dict) else None
            if isinstance(items, list) and items:
                first = items[0] if isinstance(items[0], dict) else {}
                name = (first.get('packName') or '').strip()
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    if not name:
        return 'images/card.png'

    # Vários packs no carrinho: usar o primeiro para a miniatura
    segment = name.split(',')[0].strip().lower()
    full = name.lower()

    def pick(seg):
        # Zforce 4 1000cc antes de "zforce" simples
        if 'zforce 4' in seg or '4 1000' in seg:
            return _PACK_GALLERY['zforce_4']
        if 'cf buggy' in seg:
            return _PACK_GALLERY['cf_buggy']
        if 'cf moto' in seg:
            return _PACK_GALLERY['cf_moto']
        if 'zforce' in seg:
            return _PACK_GALLERY['zforce']
        return None

    path = pick(segment) or pick(full)
    return path or 'images/card.png'


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
        path = _pack_image_url(obj.pack_name, obj.addons)
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
        count = 0
        for b in queryset:
            if b.status != 'confirmed':
                b.status = 'confirmed'
                b.save(update_fields=['status'])
                send_booking_update_email(
                    b,
                    headline='A sua reserva foi confirmada.',
                    changed_fields=['Status: Confirmada'],
                )
                count += 1
        self.message_user(request, f'{count} reserva(s) aprovada(s) e notificadas por email.')
    approve_bookings.short_description = '✅ Aprovar reservas selecionadas'

    def cancel_bookings(self, request, queryset):
        count = 0
        for b in queryset:
            if b.status != 'cancelled':
                b.status = 'cancelled'
                b.save(update_fields=['status'])
                send_booking_update_email(
                    b,
                    headline='A sua reserva foi cancelada.',
                    changed_fields=['Status: Cancelada'],
                )
                count += 1
        self.message_user(request, f'{count} reserva(s) cancelada(s) e notificadas por email.')
    cancel_bookings.short_description = '❌ Cancelar reservas selecionadas'

    def mark_completed(self, request, queryset):
        count = 0
        for b in queryset:
            if b.status != 'completed':
                b.status = 'completed'
                b.save(update_fields=['status'])
                send_booking_update_email(
                    b,
                    headline='A sua reserva foi marcada como concluída. Obrigado!',
                    changed_fields=['Status: Concluída'],
                )
                count += 1
        self.message_user(request, f'{count} reserva(s) marcada(s) como concluída(s) e notificadas por email.')
    mark_completed.short_description = '✓ Marcar como concluídas'

    def save_model(self, request, obj, form, change):
        changed = []
        headline = None
        if change and obj.pk:
            try:
                old = Booking.objects.get(pk=obj.pk)
                if old.status != obj.status:
                    changed.append(f'Status: {old.get_status_display()} → {obj.get_status_display()}')
                if old.booking_date != obj.booking_date:
                    o = old.booking_date.strftime('%d/%m/%Y') if old.booking_date else 'A definir'
                    n = obj.booking_date.strftime('%d/%m/%Y') if obj.booking_date else 'A definir'
                    changed.append(f'Data do tour: {o} → {n}')
                if old.pack_name != obj.pack_name:
                    changed.append('Pack(s): atualizado')
                if old.pack_price != obj.pack_price:
                    changed.append('Preço total: atualizado')
                if (old.addons or '') != (obj.addons or ''):
                    changed.append('Detalhes: atualizado')
            except Booking.DoesNotExist:
                pass

            if changed:
                headline = 'A sua reserva foi atualizada pela nossa equipa.'

        super().save_model(request, obj, form, change)

        if change and changed:
            send_booking_update_email(obj, headline=headline, changed_fields=changed)

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
