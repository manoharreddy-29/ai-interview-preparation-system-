-- AI-Based Student Answer Evaluation System
-- MySQL Schema and Initial Seed Data

CREATE DATABASE IF NOT EXISTS `student_eval_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `student_eval_db`;

-- 1. Users Table (Students & Faculty)
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(150) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('student', 'faculty') NOT NULL,
    `identifier` VARCHAR(100) NOT NULL, -- Student Roll No or Faculty Employee ID
    `department` VARCHAR(100) DEFAULT 'Computer Science',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Questions Table
CREATE TABLE IF NOT EXISTS `questions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `faculty_id` INT NULL,
    `faculty_name` VARCHAR(150) DEFAULT 'Faculty Administrator',
    `title` VARCHAR(255) NOT NULL,
    `subject` VARCHAR(100) NOT NULL,
    `question_text` TEXT NOT NULL,
    `reference_answer` TEXT NOT NULL,
    `keywords` TEXT NOT NULL, -- Comma-separated or JSON string
    `max_marks` DECIMAL(5, 2) DEFAULT 10.00,
    `difficulty` VARCHAR(20) DEFAULT 'Medium',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_questions_faculty` FOREIGN KEY (`faculty_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Evaluations / Submissions Table
CREATE TABLE IF NOT EXISTS `evaluations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `student_name` VARCHAR(150) NOT NULL,
    `student_identifier` VARCHAR(100) NOT NULL,
    `student_department` VARCHAR(100) DEFAULT 'Computer Science',
    `question_id` INT NULL,
    `question_title` VARCHAR(255) NOT NULL,
    `student_answer` TEXT NOT NULL,
    `marks_obtained` DECIMAL(5, 2) NOT NULL,
    `max_marks` DECIMAL(5, 2) NOT NULL,
    `score_percentage` DECIMAL(5, 2) NOT NULL,
    `rating` VARCHAR(50) NOT NULL,
    `summary` TEXT NOT NULL,
    `remarks` TEXT NOT NULL,
    `strengths` TEXT NOT NULL,        -- JSON array
    `improvements` TEXT NOT NULL,    -- JSON array
    `suggestions` TEXT NOT NULL,     -- JSON array
    `matched_keywords` TEXT NOT NULL,
    `missing_keywords` TEXT NOT NULL,
    `evaluation_engine` VARCHAR(100) DEFAULT 'Gemini AI',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_evaluations_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Initial Seed Data: Default Demo Faculty and Student (Passwords: 'student123' and 'faculty123')
-- SHA-256 hashes:
-- student123 -> a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
-- faculty123 -> ec5b642e03be81a74e50882ef9ff8ecb2f90a19e5988ad996515ba8ec63df99e
INSERT IGNORE INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `identifier`, `department`) VALUES
(1, 'Dr. Evelyn Reed', 'faculty@demo.com', 'ec5b642e03be81a74e50882ef9ff8ecb2f90a19e5988ad996515ba8ec63df99e', 'faculty', 'FAC-8812', 'Computer Science & Engineering'),
(2, 'Alex Morgan', 'student@demo.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'student', 'CS2026-042', 'Computer Science & Engineering');

-- Seed Sample Questions
INSERT IGNORE INTO `questions` (`id`, `faculty_id`, `faculty_name`, `title`, `subject`, `question_text`, `reference_answer`, `keywords`, `max_marks`, `difficulty`) VALUES
(1, 1, 'Dr. Evelyn Reed', 'Core Principles of OOP', 'Object Oriented Programming', 'Explain the four core principles of Object-Oriented Programming (OOP) and briefly describe their significance in software design.', 'The four core principles of Object-Oriented Programming are Encapsulation, Abstraction, Inheritance, and Polymorphism. Encapsulation binds together data and functions into a single unit (class) and restricts direct access to internal state, promoting data hiding and security. Abstraction hides complex implementation details and exposes only the essential features to the user, typically via interfaces and abstract classes. Inheritance enables a child class to inherit properties and behaviors from a parent class, facilitating code reusability and hierarchical organization. Polymorphism allows objects to take multiple forms and respond differently to the same method call, achieved through method overloading (compile-time) and method overriding (runtime).', 'encapsulation, abstraction, inheritance, polymorphism, code reusability, data hiding', 10.00, 'Medium'),

(2, 1, 'Dr. Evelyn Reed', 'Database Normalization & 3NF', 'Database Management Systems', 'Define database normalization and explain the conditions required for a relation to be in Third Normal Form (3NF).', 'Database normalization is the process of structuring a relational database to minimize data redundancy and prevent insertion, update, and deletion anomalies. For a relation to achieve Third Normal Form (3NF), it must first satisfy Second Normal Form (2NF), meaning it is in 1NF and all non-key attributes are fully functionally dependent on the primary key. Second, every non-prime attribute in the relation must not be transitively dependent on any candidate key. In formal terms, for every non-trivial functional dependency X -> Y, either X is a superkey or Y is a prime attribute (part of a candidate key). Normalizing to 3NF ensures data integrity and storage efficiency.', 'normalization, 3nf, third normal form, 2nf, functional dependency, transitive dependency, superkey, prime attribute, data redundancy, anomalies', 10.00, 'Hard'),

(3, 1, 'Dr. Evelyn Reed', 'Supervised vs Unsupervised Learning', 'Artificial Intelligence & ML', 'Distinguish between supervised and unsupervised machine learning paradigms, providing representative examples for each.', 'Supervised machine learning algorithms learn from labeled training datasets where input features are paired with ground-truth target outputs or class labels. The objective is to learn a mapping function from inputs to outputs to predict targets on unseen data. Core sub-types include classification (e.g., spam detection, image classification) and regression (e.g., house price forecasting). In contrast, unsupervised learning processes unlabeled datasets without explicit target supervisory signals. The algorithm identifies latent patterns, clustering structures, or intrinsic dimensional representations on its own. Common tasks include clustering (e.g., K-Means customer segmentation) and dimensionality reduction (e.g., Principal Component Analysis).', 'supervised learning, unsupervised learning, labeled data, unlabeled data, classification, regression, clustering, patterns, k-means, target output', 10.00, 'Easy');
