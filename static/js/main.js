/* Cookbook Studio - Premium Magazine JavaScript Interactions */

document.addEventListener('DOMContentLoaded', function() {
    initScrollNavbar();
    initAutocompleteSearch();
    initIngredientsChecklist();
    initFadeInAnimations();
    initDynamicFormsets();
    initNewsletterForm();
    initRecipeLikes();
});

/* 1. Scroll-Shrink Sticky Navbar */
function initScrollNavbar() {
    const navbar = document.querySelector('.navbar-editorial');
    if (!navbar) return;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-shrink');
        } else {
            navbar.classList.remove('navbar-shrink');
        }
    });
}

/* 2. Live Search Autocomplete Suggestions */
function initAutocompleteSearch() {
    const searchInput = document.querySelector('.search-editorial');
    const dropdown = document.querySelector('.search-autocomplete-dropdown');
    
    if (!searchInput || !dropdown) return;
    
    let debounceTimer;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = searchInput.value.trim();
        
        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }
        
        debounceTimer = setTimeout(() => {
            fetch(`/api/search-autocomplete/?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    dropdown.innerHTML = '';
                    if (data.results && data.results.length > 0) {
                        data.results.forEach(item => {
                            const div = document.createElement('div');
                            div.className = 'autocomplete-item';
                            div.innerHTML = `
                                <span>${item.title}</span>
                                <span class="type-badge">${item.type}</span>
                            `;
                            div.addEventListener('click', () => {
                                window.location.href = item.url;
                            });
                            dropdown.appendChild(div);
                        });
                        dropdown.style.display = 'block';
                    } else {
                        dropdown.style.display = 'none';
                    }
                })
                .catch(err => console.error("Autocomplete error:", err));
        }, 300);
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

/* 3. Interactive Ingredients Checklist */
function initIngredientsChecklist() {
    const checklistItems = document.querySelectorAll('.ingredient-item');
    checklistItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (!checkbox) return;
        
        item.addEventListener('click', function(e) {
            // Prevent double triggers if clicked on label/checkbox directly
            if (e.target.tagName !== 'INPUT') {
                checkbox.checked = !checkbox.checked;
                checkbox.dispatchEvent(new Event('change'));
            }
        });
        
        checkbox.addEventListener('change', function() {
            if (checkbox.checked) {
                item.classList.add('checked');
            } else {
                item.classList.remove('checked');
            }
        });
    });
}

/* 4. Intersection Observer for Fade-In Effects */
function initFadeInAnimations() {
    const sections = document.querySelectorAll('.fade-in-section');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        sections.forEach(sec => observer.observe(sec));
    } else {
        // Fallback for older browsers
        sections.forEach(sec => sec.classList.add('is-visible'));
    }
}

/* 5. Dynamic Steps & Ingredients Builders for Create/Edit Recipe */
function initDynamicFormsets() {
    // Ingredients
    const addIngBtn = document.getElementById('add-ingredient-btn');
    const ingContainer = document.getElementById('ingredients-container');
    const totalIngForms = document.getElementById('id_ingredients-TOTAL_FORMS');
    
    if (addIngBtn && ingContainer && totalIngForms) {
        addIngBtn.addEventListener('click', function() {
            const formCount = parseInt(totalIngForms.value);
            const emptyTemplate = document.getElementById('empty-ingredient-form').innerHTML;
            const newFormHtml = emptyTemplate.replace(/__prefix__/g, formCount);
            
            const div = document.createElement('div');
            div.className = 'form-row-dynamic ingredient-form-row';
            div.innerHTML = newFormHtml;
            ingContainer.appendChild(div);
            
            totalIngForms.value = formCount + 1;
        });
    }
    
    // Steps
    const addStepBtn = document.getElementById('add-step-btn');
    const stepContainer = document.getElementById('steps-container');
    const totalStepForms = document.getElementById('id_steps-TOTAL_FORMS');
    
    if (addStepBtn && stepContainer && totalStepForms) {
        addStepBtn.addEventListener('click', function() {
            const formCount = parseInt(totalStepForms.value);
            const emptyTemplate = document.getElementById('empty-step-form').innerHTML;
            const newFormHtml = emptyTemplate.replace(/__prefix__/g, formCount);
            
            const div = document.createElement('div');
            div.className = 'form-row-dynamic step-form-row';
            div.innerHTML = newFormHtml;
            stepContainer.appendChild(div);
            
            totalStepForms.value = formCount + 1;
            
            // Auto-assign step number value
            const stepNumField = div.querySelector('.step-number-field');
            if (stepNumField) {
                stepNumField.value = formCount + 1;
            }
        });
    }
    
    // Event delegation to remove dynamic rows (sets DELETE input check to true and hides the row)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-remove-row') || e.target.closest('.btn-remove-row')) {
            const btn = e.target.classList.contains('btn-remove-row') ? e.target : e.target.closest('.btn-remove-row');
            const row = btn.closest('.form-row-dynamic');
            if (!row) return;
            
            const deleteInput = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
            if (deleteInput) {
                deleteInput.checked = true;
                row.style.display = 'none';
            } else {
                row.remove();
            }
        }
    });
}

/* 6. Newsletter Subscription Handler */
function initNewsletterForm() {
    const form = document.getElementById('newsletter-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const emailInput = form.querySelector('input[type="email"]');
        const alertBox = document.getElementById('newsletter-alert');
        
        if (!emailInput || !emailInput.value.trim()) return;
        
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData();
        formData.append('email', emailInput.value);
        formData.append('csrfmiddlewaretoken', csrfToken);
        
        fetch('/newsletter/subscribe/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(res => res.json())
        .then(data => {
            alertBox.style.display = 'block';
            alertBox.className = 'alert mt-3';
            if (data.status === 'success') {
                alertBox.classList.add('alert-success');
                emailInput.value = '';
            } else if (data.status === 'info') {
                alertBox.classList.add('alert-warning');
            } else {
                alertBox.classList.add('alert-danger');
            }
            alertBox.innerText = data.message;
            setTimeout(() => {
                alertBox.style.display = 'none';
            }, 5000);
        })
        .catch(err => console.error("Newsletter subscription error:", err));
    });
}

/* 7. Recipe Likes Toggle Handler */
function initRecipeLikes() {
    const likeBtn = document.getElementById('like-recipe-btn');
    if (!likeBtn) return;
    
    likeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const recipeSlug = likeBtn.getAttribute('data-recipe-slug');
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/recipes/${recipeSlug}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(res => res.json())
        .then(data => {
            const countLabel = document.getElementById('like-count-label');
            const heartIcon = likeBtn.querySelector('.heart-icon');
            
            if (countLabel) countLabel.innerText = data.like_count;
            
            if (data.liked) {
                heartIcon.classList.remove('bi-heart');
                heartIcon.classList.add('bi-heart-fill', 'text-danger');
            } else {
                heartIcon.classList.remove('bi-heart-fill', 'text-danger');
                heartIcon.classList.add('bi-heart');
            }
        })
        .catch(err => console.error("Likes toggle error:", err));
    });
}
