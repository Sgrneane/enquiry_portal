from rest_framework import serializers
from .models import Complain
class ComplainSerializer(serializers.ModelSerializer):
    complain_status = serializers.SerializerMethodField()
    complain_priority = serializers.SerializerMethodField()
    complain_category=serializers.SerializerMethodField()
    class Meta:
        model=Complain
        fields= '__all__'
    def get_complain_status(self, obj):
        return obj.get_status()

    def get_complain_priority(self, obj):
        return obj.get_priority()
    def get_complain_category(self,obj):
        return obj.broad_category.english_name
    
    def to_representation(self,instance):
        obj = instance 
        representation = super().to_representation(instance)
        if obj.created_by==None:
            representation['fullname']=(obj.is_anonymous.first_name + " " + obj.is_anonymous.last_name)
            representation['pnone_number']=obj.is_anonymous.phone_number
            representation['address']=(obj.is_anonymous.address)
        else:
            representation['fullname']=(obj.created_by.first_name + " " + obj.created_by.last_name)
            representation['pnone_number']=obj.created_by.phone_number
            representation['address']=(obj.created_by.address)
        return representation




