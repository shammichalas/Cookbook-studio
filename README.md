# Cookbook Studio 🍽️
> A premium, full-stack cooking blog and digital cookbook platform featuring luxury food magazine aesthetics, interactive recipe creation, PDF cookbook generation, search capabilities, user profiles, and active discussions.

---

## ✨ Features

*   **📰 Editorial Homepage**: 
    *   Sticky glassmorphism navbar.
    *   Large hero section with live search autocomplete suggestions.
    *   Spotlight sections for featured recipes (Editor's Pick), popular categories, and kitchen masters (popular chefs).
    *   AJAX-driven newsletter subscription.
*   **👩‍🍳 User Profile & Dashboard**:
    *   Detailed chef profile cards (bios, profile image uploads, follow/unfollow buttons, follower metrics).
    *   Unified tabbed panels listing published recipes, draft archives, favorited recipes, and curated cookbooks.
    *   Consolidated analytics displaying total views and likes across the chef's recipes.
*   **🍳 Interactive Recipe Layouts**:
    *   Clean layout showing preparation/cooking duration, servings, difficulty level, and calories.
    *   Interactive checklist for ingredients (strikes out items when checked off).
    *   Cooking method steps including step-by-step instructions, media images, and custom chef tips.
    *   Appreciation counter (likes system) and sidebar cookbook inclusion indicators.
    *   Automatic categories-matching recipe recommendations list.
*   **📚 Curated Cookbooks**:
    *   Users can group multiple recipes into customizable digital cookbooks with cover titles, cover images, and descriptions.
*   **📄 Print-Ready PDF Generator**:
    *   Compiles collections into structured A4 PDF ebooks via ReportLab.
    *   Includes styled cover pages, auto-generated Tables of Contents, checklist ingredient tables, instruction steps, nutrition panels, and dynamic "Page X of Y" page numbers.
*   **💬 Nested Chef Discussions**:
    *   Supports threaded, nested replies (parent comment relationships) allowing users to join the culinary conversation.

---

## 🛠️ Technology Stack

*   **Backend**: Django 5.2 (Python)
*   **Database**: PostgreSQL (production-ready) & SQLite3 (default local fallback)
*   **PDF Generation**: ReportLab
*   **Rich Text Editor**: Django CKEditor 5
*   **Frontend UI**: Vanilla CSS (Custom editorial stylesheets) & Bootstrap 5
*   **Icons**: Bootstrap Icons

---

## 📂 Project Structure

```text
cookbook_studio/          # Core configurations and settings
recipes/                  # Recipes, Categories, Tags, and Comments app
cookbooks/                # Collections management & ReportLab PDF compiler
users/                    # Custom User Model, Profiles, and Followers app
static/                   # Custom styles, scripts, and static assets
templates/                # Modular editorial HTML templates
```

---

## 🗄️ Database Relationships

The platform maps associations using custom Django models:

*   **One-to-One (`1:1`)**:
    *   `User` ⟷ `Profile` (stores bio, profile image, and created date).
*   **Many-to-One (`N:1`)**:
    *   `Recipe` ⟶ `User` (author)
    *   `Recipe` ⟶ `Category`
    *   `RecipeIngredient` ⟶ `Recipe`
    *   `RecipeStep` ⟶ `Recipe`
    *   `RecipeComment` ⟶ `Recipe` (also links recursively to `self` as a `parent` for nested replies).
    *   `RecipeLike` ⟶ `Recipe` & `User` (tracks user likes).
*   **Many-to-Many (`M:N`)**:
    *   `Recipe` ⟷ `Tag`
    *   `Cookbook` ⟷ `Recipe`
    *   `Profile` ⟷ `Profile` (handles follower relationship).

---

## 🚀 Local Installation & Setup

Follow these steps to run Cookbook Studio locally:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/shammichalas/Cookbook-studio.git
    cd Cookbook-studio
    ```

2.  **Set Up Virtual Environment**:
    ```bash
    python -m venv .venv
    # Windows activation:
    .venv\Scripts\activate
    # macOS/Linux activation:
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Migration**:
    ```bash
    python manage.py migrate
    ```

5.  **Create a Superuser** (for Admin access):
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run Development Server**:
    ```bash
    python manage.py runserver
    ```
    Access the application locally at `http://127.0.0.1:8000/`.

---

## 🧪 Running Unit Tests

The test suite validates views, user authentication flow, recipe details, and PDF utility engines.
```bash
python manage.py test
```

---

## ⚡ Supabase Integration

Cookbook Studio integrates with Supabase in two ways:

### 1. PostgreSQL Database (Recommended)
You can use Supabase as your managed PostgreSQL database. Uncomment the Supabase PostgreSQL variables in your `.env` file and replace `your-supabase-db-password` with your database password:

```env
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-supabase-db-password
DB_HOST=db.ikctffssrpazxupxthrg.supabase.co
DB_PORT=6543
```

When these environment variables are uncommented in `.env`, the Django server dynamically switches to use the remote Supabase database instead of the local SQLite file.

### 2. Python Supabase SDK
The project has the official `supabase` Python SDK installed. You can import the initialized client from [supabase_client.py](file:///d:/Django%20project/cookbook_studio/supabase_client.py) to perform direct API calls (e.g., querying tables, uploading to Supabase Storage buckets, or integrating Supabase Auth):

```python
from cookbook_studio.supabase_client import supabase

# Example: Fetching records from a custom Supabase table
response = supabase.table('todos').select("*").execute()
todos = response.data
```

