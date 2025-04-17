from rest_framework import serializers

class BlockRecommendRequestSerializer(serializers.Serializer):
    type = serializers.CharField(required=False, allow_blank=True, default='')
    category = serializers.CharField(required=False, allow_blank=True, default='')
    speaker = serializers.CharField(required=False, allow_blank=True, default='')
    listener = serializers.CharField(required=False, allow_blank=True, default='')
    instruction = serializers.CharField(required=False, allow_blank=True, default='')
    form = serializers.CharField(required=False, allow_blank=True, default='')
    excluded = serializers.CharField(required=False, allow_blank=True, default='')
    required = serializers.CharField(required=False, allow_blank=True, default='')

class RecordSerializer(serializers.Serializer):
    type = serializers.CharField(allow_blank=True, default='')
    category = serializers.CharField(allow_blank=True, default='')
    speaker = serializers.CharField(allow_blank=True, default='')
    listener = serializers.CharField(allow_blank=True, default='')
    instruction = serializers.CharField(allow_blank=True, default='')
    form = serializers.CharField(allow_blank=True, default='')
    excluded = serializers.CharField(allow_blank=True, default='')
    required = serializers.CharField(allow_blank=True, default='')

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