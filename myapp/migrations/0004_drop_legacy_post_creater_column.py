from django.db import migrations


def _drop_legacy_creater_column_forward(apps, schema_editor):
    connection = schema_editor.connection
    table_name = "myapp_post"

    with connection.cursor() as cursor:
        table_names = connection.introspection.table_names(cursor)
        if table_name not in table_names:
            return

        columns = [
            column.name
            for column in connection.introspection.get_table_description(cursor, table_name)
        ]

    if "creater_id" not in columns:
        return

    schema_editor.execute("PRAGMA foreign_keys=OFF;")
    schema_editor.execute(
        """
        CREATE TABLE myapp_post_new (
            id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            title varchar(200) NOT NULL,
            content text NOT NULL,
            attachment varchar(100) NULL,
            created_at datetime NOT NULL,
            group_type varchar(20) NOT NULL,
            max_students_per_group integer NULL,
            author_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED,
            deadline datetime NOT NULL
        );
        """
    )
    schema_editor.execute(
        """
        INSERT INTO myapp_post_new (
            id, title, content, attachment, created_at, group_type,
            max_students_per_group, author_id, deadline
        )
        SELECT
            id, title, content, attachment, created_at, group_type,
            max_students_per_group, author_id, deadline
        FROM myapp_post;
        """
    )
    schema_editor.execute("DROP TABLE myapp_post;")
    schema_editor.execute("ALTER TABLE myapp_post_new RENAME TO myapp_post;")
    schema_editor.execute(
        "CREATE INDEX myapp_post_author_id_b19d7e7f ON myapp_post(author_id);"
    )
    schema_editor.execute("PRAGMA foreign_keys=ON;")


def _drop_legacy_creater_column_backward(apps, schema_editor):
    connection = schema_editor.connection
    table_name = "myapp_post"

    with connection.cursor() as cursor:
        table_names = connection.introspection.table_names(cursor)
        if table_name not in table_names:
            return

        columns = [
            column.name
            for column in connection.introspection.get_table_description(cursor, table_name)
        ]

    if "creater_id" in columns:
        return

    schema_editor.execute("PRAGMA foreign_keys=OFF;")
    schema_editor.execute(
        """
        CREATE TABLE myapp_post_oldshape (
            id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            title varchar(200) NOT NULL,
            content text NOT NULL,
            attachment varchar(100) NULL,
            created_at datetime NOT NULL,
            group_type varchar(20) NOT NULL,
            max_students_per_group integer NULL,
            author_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED,
            deadline datetime NOT NULL,
            creater_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
        );
        """
    )
    schema_editor.execute(
        """
        INSERT INTO myapp_post_oldshape (
            id, title, content, attachment, created_at, group_type,
            max_students_per_group, author_id, deadline, creater_id
        )
        SELECT
            id, title, content, attachment, created_at, group_type,
            max_students_per_group, author_id, deadline, author_id
        FROM myapp_post;
        """
    )
    schema_editor.execute("DROP TABLE myapp_post;")
    schema_editor.execute("ALTER TABLE myapp_post_oldshape RENAME TO myapp_post;")
    schema_editor.execute(
        "CREATE INDEX myapp_post_author_id_b19d7e7f ON myapp_post(author_id);"
    )
    schema_editor.execute(
        "CREATE INDEX myapp_post_creater_id_196549ba ON myapp_post(creater_id);"
    )
    schema_editor.execute("PRAGMA foreign_keys=ON;")


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("myapp", "0003_fix_profile_role_default_and_post_group_column"),
    ]

    operations = [
        migrations.RunPython(
            _drop_legacy_creater_column_forward,
            _drop_legacy_creater_column_backward,
        ),
    ]
