class MultiDBRouter:
    """
    A database router to manage multiple databases: default (MySQL) and secondary (PostgreSQL).
    """
    def db_for_read(self, model, **hints):
        """
        Direct read operations to the appropriate database.
        """
        if model._meta.app_label == 'secondary':  # 특정 앱은 PostgreSQL로 읽기
            return 'secondary'
        return 'default'  # 기본적으로 MySQL로 읽기

    def db_for_write(self, model, **hints):
        """
        Direct write operations to the appropriate database.
        """
        if model._meta.app_label == 'secondary':  # 특정 앱은 PostgreSQL로 쓰기
            return 'secondary'
        return 'default'  # 기본적으로 MySQL로 쓰기

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects in the same database.
        """
        db_set = {'default', 'secondary'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure migrations are applied to the correct database.
        """
        if app_label == 'secondary':  # 특정 앱은 PostgreSQL에 마이그레이션
            print("tlqkffusdk")
            return db == 'secondary'
        return db == 'default'  # 기본적으로 MySQL에 마이그레이션
