from rest_framework import serializers

class BlockRecommendRequestSerializer(serializers.Serializer):
    타입 = serializers.CharField(required=False, allow_blank=True, default='')
    카테고리 = serializers.CharField(required=False, allow_blank=True, default='')
    화자 = serializers.CharField(required=False, allow_blank=True, default='')
    청자 = serializers.CharField(required=False, allow_blank=True, default='')
    지시 = serializers.CharField(required=False, allow_blank=True, default='')
    형식 = serializers.CharField(required=False, allow_blank=True, default='')
    제외 = serializers.CharField(required=False, allow_blank=True, default='')
    필수 = serializers.CharField(required=False, allow_blank=True, default='')

class RecordSerializer(serializers.Serializer):
    타입 = serializers.CharField(allow_blank=True, default='')
    카테고리 = serializers.CharField(allow_blank=True, default='')
    화자 = serializers.CharField(allow_blank=True, default='')
    청자 = serializers.CharField(allow_blank=True, default='')
    지시 = serializers.CharField(allow_blank=True, default='')
    형식 = serializers.CharField(allow_blank=True, default='')
    제외 = serializers.CharField(allow_blank=True, default='')
    필수 = serializers.CharField(allow_blank=True, default='')

    def to_representation(self, instance):
        # None 값을 빈 문자열로 변환
        return {
            field_name: str(value) if value is not None else ''
            for field_name, value in instance.items()
        }

class SimilarRecordSerializer(serializers.Serializer):
    record = RecordSerializer()
    similarity_score = serializers.FloatField()

    def to_representation(self, instance):
        return {
            'record': self.fields['record'].to_representation(instance['record']),
            'similarity_score': float(instance['similarity_score'])
        }

class BlockRecommendResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    similar_records = SimilarRecordSerializer(many=True)
    recommendations = serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField(allow_blank=True),
            allow_empty=True
        ),
        allow_empty=True
    )

    def to_representation(self, instance):
        return {
            'status': instance['status'],
            'similar_records': [
                self.fields['similar_records'].child.to_representation(record)
                for record in instance['similar_records']
            ],
            'recommendations': {
                field: [str(value) for value in values]
                for field, values in instance['recommendations'].items()
            }
        } 