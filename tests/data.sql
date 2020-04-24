-- Mock Data For Tests

INSERT INTO users (email, password, role, last_name, first_name, major)
VALUES ('teacher@stevenscollege.edu', 'pbkdf2:sha256:150000$YKTR53od$3956727084a9d3470d800ca00005a2258bde5affab208eb9ae211c46a28f575d', 'teacher', 'Fedjona', 'Zachiberto', 'CSET'),
       ('student@stevenscollege.edu', 'pbkdf2:sha256:150000$db49oioE$95b37dfa834211006b45fddfa03debdca5d2ccf49486bb7e35af144406d51c8a', 'student', 'Lueklee', 'Kevstice', 'CSET');

INSERT INTO courses (course_code, course_name, major, description, teacher_id)
VALUES ('180', 'Big Software Energy', 'CSET', 'A class that really makes you FEEL like a developer', 1),
       ('500', 'Brick smashing', 'MASN', 'Smashing bricks and smashing brick sciences', 1),
       ('155', 'Bigger Software Energy', 'CSET', 'Big boi energy', 1);

INSERT INTO sessions (session_name, meeting_days, meeting_place, meeting_time, course_id)
VALUES ('A', 'MTWThF', 'Greenfield', '12:00-16:30', 1),
       ('B', 'M', 'Remote', '12:01-16:31', 1);


INSERT INTO roster (student_id, session_id)
VALUES (2, 1),
       (2, 2);

INSERT INTO assignments (name, description, points, course_id)
VALUES ('Big Software', 'You need to create some big software with lots of big software energy', 200, 1),
       ('Bigger Software', 'You need to create some big software with lots of big software energy', 300, 1),
       ('Biggest Software', 'You need to create some big software with lots of big software energy', 400, 1),
       ('Mondo Software', 'Very mondo my dude', 25, 1),
       ('Breaking bricks', 'Break a brick on your head', 600, 2);

INSERT INTO session_assignments (session_id, assignment_id, due_date)
VALUES (1, 1, '4/25/2020'),
       (1, 2, '4/30/2020'),
       (1, 3, '5/02/2020'),
       (2, 4, '08/01/2020');

INSERT INTO assignment_grades (owner_id, assigned_id, grades)
VALUES (2, 1, 150);
