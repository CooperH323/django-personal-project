from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Pet

# Create your tests here.
class PetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        #makes a fake user
        cls.user = get_user_model().objects.create_user(
            username='testuser', email='test@email.com', password='secret'
        )
        #makes a fake post by that user
        cls.post = Pet.objects.create(
            Type='cool gato',
            description='funny gato',
            owner=cls.user
        )

    def test_pet_model(self):
        self.assertEqual(self.post.Type, 'cool gato')
        self.assertEqual(self.post.description, 'funny gato')
        self.assertEqual(self.post.owner.username, 'testuser')
        self.assertEqual(str(self.post), 'cool gato')
        self.assertEqual(self.post.get_absolute_url(), '/pets/1/')
        
    #checks to see if hompage exists
    def test_url_exists_at_correct_location_listview(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
    #checks to make sure post webpage exists
    def test_url_exists_at_correct_location_detialview(self):
        response = self.client.get('/pets/1/')
        self.assertEqual(response.status_code, 200)

    def test_post_listview(self):
        response= self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cool gato')
        self.assertTemplateUsed(response, 'home.html')

    def test_post_detailview(self):
        response = self.client.get(reverse('pet_detail', kwargs={'pk': self.post.pk}))
        no_response = self.client.get('/pet/100000/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, 'funny gato')
        self.assertTemplateUsed(response, 'pet_detail.html')

    def test_post_createview(self):
        response = self.client.post(
            reverse("pet_new"),
            {
                "Type": "New Type",
                "description": "New description",
                "owner": self.user.id
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Pet.objects.last().Type, "New Type")
        self.assertEqual(Pet.objects.last().description, "New description")

    def test_pet_updateview(self):
            response = self.client.post(
                reverse("pet_edit", args="1"),
                {
                    "Type": "Updated Type",
                    "description": "Updated description",
                }
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Pet.objects.last().Type, "Updated Type")
            self.assertEqual(Pet.objects.last().description, "Updated description")

    def test_pet_deleteview(self):
        response = self.client.post(reverse("pet_delete", args="1"))
        self.assertEqual(response.status_code, 302)

    def test_vote_anonymous_user_fails(self):
        """Verifies that an unauthenticated user cannot vote and gets an error."""
        # Create a second pet since voting requires 2 pets
        pet2 = Pet.objects.create(Type='dog', description='golden', owner=self.user)
        
        response = self.client.post(reverse('home'), {'selected_pets': [self.post.id, pet2.id]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("You must be logged in to vote!", response.context['error_message'])

    def test_vote_incorrect_count_fails(self):
        """Verifies that selecting anything other than exactly 2 pets causes a validation error."""
        self.client.force_login(self.user)
        
        # Submitting only 1 pet
        response = self.client.post(reverse('home'), {'selected_pets': [self.post.id]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("You must select exactly 2 pets to vote!", response.context['error_message'])

    def test_vote_success(self):
        """Verifies successful simultaneous voting for exactly 2 pets when logged in."""
        self.client.force_login(self.user)
        pet2 = Pet.objects.create(Type='Fish', description='do a flip!!!!', owner=self.user)

        response = self.client.post(reverse('home'), {'selected_pets': [self.post.id, pet2.id]})
        
        # Should redirect back home on success
        self.assertRedirects(response, reverse('home'))
        
        # Refresh from database to ensure the Many-to-Many table records the user's vote
        self.post.refresh_from_db()
        pet2.refresh_from_db()
        
        # Assert that the voter relationship counts are correctly tracked in the database
        self.assertEqual(self.post.voters.count(), 1)
        self.assertEqual(pet2.voters.count(), 1)
        
        # Explicitly verify that our specific user is recorded inside both voters relations
        self.assertTrue(self.post.voters.filter(id=self.user.id).exists())
        self.assertTrue(pet2.voters.filter(id=self.user.id).exists())


    def test_vote_duplicate_fails(self):
        """Verifies that a user cannot vote for a pet they have already voted for."""
        self.client.force_login(self.user)
        pet2 = Pet.objects.create(Type='dog', description='spinnnnn', owner=self.user)

        # Apply an initial successful vote
        self.client.post(reverse('home'), {'selected_pets': [self.post.id, pet2.id]})

        # Attempt to vote a second time with the same selection
        response = self.client.post(reverse('home'), {'selected_pets': [self.post.id, pet2.id]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("You have already voted for", response.context['error_message'])
