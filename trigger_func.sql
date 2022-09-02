SELECT id, name, age, address, phone, email, country, date_of_birth, team_member, is_monitored
	FROM public."user";
SELECT id, uid, name, age, address, phone, email, country, date_of_birth, team_member, is_monitored, refresh_datetime
	FROM public.user_history;
	
UPDATE public."user"
SET name = 'Omar Fessi'
WHERE id = 1



CREATE OR REPLACE FUNCTION log_name_changes()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN
	IF NEW.name <> OLD.name THEN
		 INSERT INTO user_history(uid,name,age,address,phone,email,country,date_of_birth,team_member,is_monitored, refresh_datetime )
		 VALUES(OLD.id,OLD.name,OLD.age, OLD.address, OLD.phone, OLD.email, OLD.country, OLD.date_of_birth, OLD.team_member, OLD.is_monitored, now());
	END IF;

	RETURN NEW;
END;
$$

CREATE TRIGGER name_changes
  AFTER INSERT OR UPDATE
  ON public."user"
  FOR EACH ROW
  EXECUTE PROCEDURE log_name_changes();


BEGIN
	IF NEW.name <> OLD.name THEN
		 INSERT INTO user_history(uid,name,age,address,phone,email,country,date_of_birth,team_member,is_monitored, refresh_datetime )
		 VALUES(NEW.id,NEW.name,NEW.age, NEW.address, NEW.phone, NEW.email, NEW.country, NEW.date_of_birth, NEW.team_member, NEW.is_monitored, now());
	ELSIF OLD.id is null THEN
		INSERT INTO user_history(uid,name,age,address,phone,email,country,date_of_birth,team_member,is_monitored, refresh_datetime )
		VALUES(NEW.id,NEW.name,NEW.age, NEW.address, NEW.phone, NEW.email, NEW.country, NEW.date_of_birth, NEW.team_member, NEW.is_monitored, now());
	END IF;

	RETURN NEW;
END;



---create trigger function
BEGIN
	IF NEW.name <> OLD.name or NEW.is_monitored <> OLD.is_monitored THEN
		 INSERT INTO user_history(uid,name,age,address,phone,email,country,date_of_birth,team_member,is_monitored, refresh_datetime )
		 VALUES(NEW.id,NEW.name,NEW.age, NEW.address, NEW.phone, NEW.email, NEW.country, NEW.date_of_birth, NEW.team_member, NEW.is_monitored, now());
	ELSIF OLD.id is null THEN
		INSERT INTO user_history(uid,name,age,address,phone,email,country,date_of_birth,team_member,is_monitored, refresh_datetime )
		VALUES(NEW.id,NEW.name,NEW.age, NEW.address, NEW.phone, NEW.email, NEW.country, NEW.date_of_birth, NEW.team_member, NEW.is_monitored, now());
	END IF;

	RETURN NEW;
END;

---create trigger on the above function

CREATE TRIGGER detect_changes
    AFTER INSERT OR UPDATE 
    ON public."user"
    FOR EACH ROW
    EXECUTE PROCEDURE public.log_name_changes();