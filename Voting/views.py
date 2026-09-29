from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Pet

class PetList(ListView):
    model = Pet
    template_name = 'home.html'

    # Calculates how many OTHER users voted for each pet
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        for pet in queryset:
            # Safely gets the total count from your votes property or relation
            total_votes = getattr(pet, 'votes', 0) or pet.voters.count()
            
            # If logged in and already voted, subtract 1 from total to find "other" voters
            if user.is_authenticated and pet.voters.filter(id=user.id).exists():
                pet.other_votes = max(0, total_votes - 1)
                pet.voted_by_me = True
            else:
                pet.other_votes = total_votes
                pet.voted_by_me = False
                
        return queryset

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            self.object_list = self.get_queryset()
            context = self.get_context_data(
                error_message="You must be logged in to vote!"
            )
            return self.render_to_response(context)

        selected_pet_ids = request.POST.getlist('selected_pets')

        if len(selected_pet_ids) != 2:
            self.object_list = self.get_queryset()
            context = self.get_context_data(
                error_message=f"You must select exactly 2 pets to vote! You selected {len(selected_pet_ids)}."
            )
            return self.render_to_response(context)

        # Check if already voted
        for pet_id in selected_pet_ids:
            pet = Pet.objects.get(pk=pet_id)
            if pet.voters.filter(id=request.user.id).exists():
                self.object_list = self.get_queryset()
                context = self.get_context_data(
                    error_message=f"You have already voted for {pet.Type} before!"
                )
                return self.render_to_response(context)

        # Original voting loop with user-tracking added
        for pet_id in selected_pet_ids:
            pet = Pet.objects.get(pk=pet_id)
            if hasattr(pet, 'votes'):
                pet.votes += 1
            else:
                pet.votes = 1
            
            pet.voters.add(request.user)
            pet.save()

        return redirect('home')

class PetDetail(DetailView):
    model = Pet
    template_name = 'pet_detail.html'

class PetCreateView(CreateView):
    model = Pet
    template_name = 'pet_new.html'
    fields = ['Type', 'owner', 'description']

class PetUpdateView(UpdateView):
    model = Pet
    template_name = 'pet_edit.html'
    fields = ['Type', 'description']

class PetDeleteView(DeleteView):
    model = Pet
    template_name = 'pet_delete.html'
    success_url = reverse_lazy('home')


