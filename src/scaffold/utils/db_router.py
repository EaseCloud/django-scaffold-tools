from django.conf import settings


class AppRouter:
    db_map = getattr(settings, 'DATABASE_ROUTE_MAP', {})

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        return self.db_map.get(model._meta.app_label, 'default')

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        return self.db_map.get(model._meta.app_label, 'default')

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        return self.db_map.get(obj1._meta.app_label, 'default') == \
               self.db_map.get(obj2._meta.app_label, 'default') == 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        return self.db_map.get(app_label, 'default') == db == 'default'
