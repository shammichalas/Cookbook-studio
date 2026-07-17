from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.contrib import messages
from .models import Cookbook
from .forms import CookbookForm
from .pdf_utils import generate_cookbook_pdf

def cookbook_list(request):
    """View to list public digital cookbooks."""
    cookbooks = Cookbook.objects.all()
    return render(request, 'cookbooks/cookbook_list.html', {'cookbooks': cookbooks})

def cookbook_detail(request, slug):
    """View details of a cookbook with its recipe list."""
    cookbook = get_object_or_404(Cookbook, slug=slug)
    return render(request, 'cookbooks/cookbook_detail.html', {'cookbook': cookbook})

@login_required
def cookbook_create(request):
    """Create a new cookbook collection."""
    if request.method == 'POST':
        form = CookbookForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            cookbook = form.save(commit=False)
            cookbook.owner = request.user
            cookbook.save()
            form.save_m2m() # Save ManyToMany recipes
            messages.success(request, f"Cookbook '{cookbook.title}' created successfully!")
            return redirect('cookbook_detail', slug=cookbook.slug)
    else:
        form = CookbookForm(user=request.user)

    return render(request, 'cookbooks/cookbook_form.html', {
        'form': form,
        'title': 'Create Cookbook Collection'
    })

@login_required
def cookbook_edit(request, slug):
    """Edit an existing cookbook collection."""
    cookbook = get_object_or_404(Cookbook, slug=slug)
    if cookbook.owner != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to edit this cookbook.")
        return redirect('cookbook_detail', slug=cookbook.slug)

    if request.method == 'POST':
        form = CookbookForm(request.POST, request.FILES, instance=cookbook, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cookbook '{cookbook.title}' updated successfully!")
            return redirect('cookbook_detail', slug=cookbook.slug)
    else:
        form = CookbookForm(instance=cookbook, user=request.user)

    return render(request, 'cookbooks/cookbook_form.html', {
        'form': form,
        'cookbook': cookbook,
        'title': 'Edit Cookbook Collection'
    })

@login_required
def cookbook_delete(request, slug):
    """Delete a cookbook collection."""
    cookbook = get_object_or_404(Cookbook, slug=slug)
    if cookbook.owner != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to delete this cookbook.")
        return redirect('cookbook_detail', slug=cookbook.slug)

    if request.method == 'POST':
        cookbook.delete()
        messages.success(request, "Cookbook collection deleted successfully.")
        return redirect('profile_view', username=request.user.username)

    return render(request, 'cookbooks/cookbook_confirm_delete.html', {'cookbook': cookbook})

def generate_pdf(request, slug):
    """
    Triggers ReportLab compilation of the cookbook and
    returns it as an A4 PDF attachment.
    """
    cookbook = get_object_or_404(Cookbook, slug=slug)
    if cookbook.recipe_count == 0:
        messages.error(request, "Cannot generate PDF. This cookbook contains no recipes yet.")
        return redirect('cookbook_detail', slug=cookbook.slug)
        
    try:
        pdf_buffer = generate_cookbook_pdf(cookbook)
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        filename = f"{cookbook.slug}_cookbook.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, f"Failed to generate PDF cookbook: {e}")
        return redirect('cookbook_detail', slug=cookbook.slug)
