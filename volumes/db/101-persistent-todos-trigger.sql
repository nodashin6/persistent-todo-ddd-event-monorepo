CREATE OR REPLACE FUNCTION record_todo_history()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        -- Invalidate the old record in p_todos
        UPDATE p_todos
        SET validate_to = NEW.updated_at
        WHERE todo_id = OLD.id AND validate_to IS NULL;
    END IF;

    -- Insert the new record in p_todos
    INSERT INTO p_todos (todo_id, task, is_completed, created_at, updated_at, validate_from, validate_to)
    VALUES (NEW.id, NEW.task, NEW.is_completed, NEW.created_at, NEW.updated_at, NEW.updated_at, NULL);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER todo_history_trigger
AFTER INSERT OR UPDATE ON todos
FOR EACH ROW
EXECUTE FUNCTION record_todo_history();
