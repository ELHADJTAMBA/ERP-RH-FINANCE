from rest_framework import serializers
from .models import Site, Department


class SiteSerializer(serializers.ModelSerializer):
    department_count = serializers.IntegerField(source="departments.count", read_only=True)

    class Meta:
        model = Site
        fields = ("id", "name", "site_type", "address", "is_active", "department_count", "created_at")


class DepartmentSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source="site.name", read_only=True)
    manager_name = serializers.CharField(source="manager.get_full_name", read_only=True)

    class Meta:
        model = Department
        fields = ("id", "name", "site", "site_name", "manager", "manager_name", "is_active", "created_at")
