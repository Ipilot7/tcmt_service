from .models import Institution, Equipment

def get_institutions_list() -> QuerySet[Institution]:
    """
    Returns a queryset of all institutions.
    """
    return Institution.objects.all()

def get_equipment_list() -> QuerySet[Equipment]:
    """
    Returns a queryset of all equipment.
    """
    return Equipment.objects.all().select_related('institution')

def get_equipment_by_id(equipment_id: int) -> Equipment:
    """
    Returns an equipment instance by its ID.
    """
    return Equipment.objects.get(pk=equipment_id)
