SELECT id, name, age, address, phone, email, country, date_of_birth, team_member, is_monitored
	FROM public."user";
	
SELECT * FROM public."user_history";

UPDATE public."user_history" 
SET is_monitored =TRUE

DELETE FROM public."user_history";
DELETE FROM public."user";