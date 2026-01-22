from django.test import TestCase
from .models import Institution, Region, Equipment, EquipmentType
from .selectors import get_institutions_list, get_equipment_list
from .services import institution_create, institution_update, equipment_create, equipment_update
from .serializers import InstitutionSerializer, EquipmentSerializer

class InstitutionLayeredArchitectureTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="Test Region")
        self.eq = Equipment.objects.create(
            equipment_type=EquipmentType.objects.create(name="Type"), 
            serial_number="SN1"
        )

    def test_institution_create_service(self):
        data = institution_create(
            name="New Inst", 
            region=self.region, 
            sale_date=datetime.date(2023, 1, 1),
            equipments=[self.eq]
        )
        self.assertEqual(Institution.objects.count(), 1)
        self.assertEqual(data['name'], "New Inst")
        self.assertEqual(data['sale_date'], "2023-01-01")
        self.assertEqual(len(data['equipments']), 1)
        # Warranty logic check (2023 + 2 = 2025)
        self.assertEqual(data['warranty_end'], "2025-01-01")

    def test_institution_update_service(self):
        inst = Institution.objects.create(name="Old Name", region=self.region)
        data = institution_update(institution=inst, name="New Name", region=self.region)
        self.assertEqual(data['name'], "New Name")
        inst.refresh_from_db()
        self.assertEqual(inst.name, "New Name")

    def test_get_institutions_list_selector(self):
        Institution.objects.create(name="Inst 1", region=self.region)
        Institution.objects.create(name="Inst 2", region=self.region)
        qs = get_institutions_list()
        self.assertEqual(qs.count(), 2)

    def test_serializer(self):
        inst = Institution.objects.create(name="Serializer Test", region=self.region)
        data = InstitutionSerializer.serialize(inst)
        self.assertEqual(data['name'], "Serializer Test")
        self.assertEqual(data['region_name'], "Test Region")

class EquipmentLayeredArchitectureTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="Test Region")
        self.institution = Institution.objects.create(name="Test Inst", region=self.region)
        self.eq_type = EquipmentType.objects.create(name="Test Type")

    def test_equipment_create_service(self):
        data = equipment_create(
            equipment_type=self.eq_type, 
            serial_number="SN123"
        )
        self.assertEqual(Equipment.objects.count(), 1)
        self.assertEqual(data['equipment_type_name'], "Test Type")

    def test_equipment_update_service(self):
        eq = Equipment.objects.create(equipment_type=self.eq_type, serial_number="SN1")
        new_type = EquipmentType.objects.create(name="New Type")
        data = equipment_update(
            equipment=eq, 
            equipment_type=new_type, 
            serial_number="SN1_MOD"
        )
        self.assertEqual(data['equipment_type_name'], "New Type")
        self.assertEqual(data['serial_number'], "SN1_MOD")

    def test_get_equipment_list_selector(self):
        Equipment.objects.create(equipment_type=self.eq_type, serial_number="SN1")
        Equipment.objects.create(equipment_type=self.eq_type, serial_number="SN2")
        qs = get_equipment_list()
        self.assertEqual(qs.count(), 2)
