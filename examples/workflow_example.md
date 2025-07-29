# Spec-Driven Development Workflow Example

This example demonstrates the complete workflow from requirements generation to code implementation using the MCP Spec-Driven Development Server.

## Step 1: Generate Requirements

**Prompt**: `generate-requirements`

**Input**: "Create a simple task management web application"

**Expected Output**: A `requirements.md` file with EARS-formatted requirements like:

```markdown
# Requirements for Task Management Web Application

## Functional Requirements

**REQ-001**: WHEN a user accesses the application, the system SHALL display a list of existing tasks.

**REQ-002**: WHEN a user clicks "Add Task", the system SHALL provide a form to create a new task with title and description.

**REQ-003**: WHEN a user submits a new task, the system SHALL save the task and update the task list.

**REQ-004**: WHEN a user clicks on a task, the system SHALL allow editing of the task details.

**REQ-005**: WHEN a user marks a task as complete, the system SHALL update the task status visually.

## Non-Functional Requirements

**REQ-006**: The application SHALL be responsive and work on mobile devices.

**REQ-007**: The application SHALL load within 2 seconds on standard internet connections.
```

## Step 2: Generate Design from Requirements

**Prompt**: `generate-design-from-requirements`

**Input**: The `requirements.md` file content from Step 1

**Expected Output**: A `design.md` file with detailed technical design:

```markdown
# Design Document for Task Management Web Application

## Architecture Overview

- **Frontend**: React.js with TypeScript
- **Backend**: Node.js with Express
- **Database**: SQLite for simplicity
- **Styling**: Tailwind CSS

## Component Structure

### Frontend Components

1. **App Component**
   - Main application container
   - Manages global state

2. **TaskList Component**
   - Displays list of tasks
   - Handles task selection

3. **TaskForm Component**
   - Form for creating/editing tasks
   - Input validation

4. **TaskItem Component**
   - Individual task display
   - Toggle completion status

### Backend API Endpoints

- `GET /api/tasks` - Retrieve all tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/:id` - Update existing task
- `DELETE /api/tasks/:id` - Delete task

## Database Schema

```sql
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## File Structure

```
task-manager/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── App.tsx
│   └── package.json
├── backend/
│   ├── src/
│   │   ├── routes/
│   │   ├── models/
│   │   └── server.ts
│   └── package.json
└── README.md
```
```

## Step 3: Generate Code from Design

**Prompt**: `generate-code-from-design`

**Input**: The `design.md` file content from Step 2

**Expected Output**: Complete implementation files including:

- Frontend React components
- Backend API routes
- Database setup scripts
- Configuration files
- Package.json files
- README with setup instructions

## Complete Workflow

1. **Start with high-level idea**: "Create a simple task management web application"
2. **Generate structured requirements** using EARS format
3. **Create detailed technical design** based on requirements
4. **Generate implementation code** following the design
5. **Result**: A complete, working application ready for deployment

## Benefits of This Approach

- **Structured Development**: Clear progression from idea to implementation
- **Documentation**: Automatic generation of requirements and design docs
- **Consistency**: Standardized format ensures nothing is missed
- **Traceability**: Clear connection between requirements, design, and code
- **Quality**: Systematic approach reduces bugs and improves maintainability