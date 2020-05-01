-- TSCT Portal Database Schema
--
-- This file will drop and recreate all tables necessary for
-- the application and can be run with the `flask init-db`
-- command in your terminal.

-- Drop existing tables
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS roster;
DROP TABLE IF EXISTS assignments CASCADE;
DROP TABLE IF EXISTS session_assignments CASCADE;
DROP TABLE IF EXISTS assignment_grades CASCADE;
DROP TABLE IF EXISTS uploads CASCADE;

-- Users
CREATE TABLE users (
    id bigserial PRIMARY KEY,
    email text UNIQUE NOT NULL,
    password text NOT NULL,
    role varchar(7) NOT NULL CHECK (role IN ('teacher', 'student')),
    last_name varchar(50) NOT NULL,
    first_name varchar(50) NOT NULL,
    major varchar(5) NOT NULL
);

-- Courses
CREATE TABLE courses (
  id bigserial PRIMARY KEY,
  course_code varchar(10) NOT NULL,
  course_name text NOT NULL,
  major text NOT NULL,
  description text NOT NULL,
  -- Create a one-to-many relationship between teacher users and courses they own
  teacher_id bigint REFERENCES users(id) NOT NULL
);

-- Course Sessions
CREATE TABLE sessions (
  id bigserial PRIMARY KEY,
  session_name varchar(1),
  meeting_days TEXT,
  meeting_place TEXT,
  meeting_time varchar(11),
  -- Create a one-to-many relationship between courses and sessions of those courses
  course_id bigint NOT NULL REFERENCES courses(id) ON DELETE CASCADE
);

-- Roster
-- Create a many-to-many relationship between student users and course sessions
CREATE TABLE roster (
  -- Create a one-to-many relationship between student users and course sessions they belong to
  student_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  -- Create a one-to-many relationship between course sessions and the students that belong to it
  session_id bigint NOT NULL REFERENCES sessions(id) ON DELETE CASCADE
);

-- Assignments
CREATE TABLE assignments (
  id bigserial PRIMARY KEY,
  name varchar(100) NOT NULL,
  description text NOT NULL,
  points bigint NOT NULL,
  -- Create a one-to-many relationship between courses and assignments that belong to it
  course_id bigint NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  assignment_type varchar(25) NOT NULL
);

-- Session Assignments
-- Create a many-to-many relationship between course sessions and assignments for those sessions
CREATE TABLE session_assignments (
  -- Create ID for the specific instance of the assignment, assigned to this session
  work_id bigserial PRIMARY KEY,
  -- Create a one-to-many relationship between sessions and assignments
  session_id bigint NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  -- Create a one-to-many relationship between assignments and sessions
  assignment_id bigint NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
  due_date date
);

-- Assignment Grades
-- Create a many-to-many relationship between assigned work and students with associated grades
CREATE TABLE assignment_grades(
  -- Create a one-to-many relationship between users and their assigned work
  owner_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  -- Create a one-to-many relationship between assigned work and users
  assigned_id bigint NOT NULL REFERENCES session_assignments(work_id) ON DELETE CASCADE,
  grades varchar(100)
);

-- Uploads for Assignments
CREATE TABLE uploads(
  id bigserial PRIMARY KEY,
  upload_name TEXT NOT NULL,
  upload_id TEXT NOT NULL,
  -- Create a one-to-many relationship between uploaded files and the owner for the uploaded files
  owner_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  -- Create a one-to-many relationship between assignments and uploads
  assignment_id bigint NOT NULL REFERENCES assignments(id) ON DELETE CASCADE
);
