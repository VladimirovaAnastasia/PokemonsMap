import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.shortcuts import get_list_or_404

from .models import Pokemon
from .models import PokemonEntity

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = "https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832&fill=transparent"


def add_pokemon(folium_map, lat, lon, name, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        tooltip=name,
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    # with open("pokemon_entities/pokemons.json", encoding="utf-8") as database:
    #    pokemons = json.load(database)['pokemons']
    pokemons = Pokemon.objects.all().values()
    pokemon_entities = PokemonEntity.objects.all().values()

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    for pokemon in pokemons:
        for pokemon_entity in pokemon_entities:
            if pokemon['id'] == pokemon_entity['pokemon_id']:
                add_pokemon(
                    folium_map, pokemon_entity['lat'], pokemon_entity['lon'],
                    pokemon['title'], 'http://127.0.0.1:8000/media/' + pokemon['photo'])

    pokemons_on_page = []
    for pokemon in pokemons:
        pokemons_on_page.append({
            'pokemon_id': pokemon['id'],
            'title_ru': pokemon['title'],
            'img_url': 'http://127.0.0.1:8000/media/' + pokemon['photo'],
        })

    return render(request, "mainpage.html", context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    find_pokemons = Pokemon.objects.filter(id=int(pokemon_id)).values()
    pokemon_entities = PokemonEntity.objects.filter(pokemon_id=int(pokemon_id)).values()
    pokemon = {
        'pokemon_id': find_pokemons[0]['id'],
        'title_ru': find_pokemons[0]['title'],
        'img_url': 'http://127.0.0.1:8000/media/' + find_pokemons[0]['photo'],
        'title_en': find_pokemons[0]['title_en'],
        'title_jp': find_pokemons[0]['title_jp'],
        'description': find_pokemons[0]['description'],
    }
    if not (find_pokemons[0]['evolution_from_id'] is None):
        pokemon_parent = Pokemon.objects.filter(id=find_pokemons[0]['evolution_from_id']).values()

        pokemon.update({
            "previous_evolution": {
                'pokemon_id': pokemon_parent[0]['id'],
                'title_ru': pokemon_parent[0]['title'],
                'img_url': 'http://127.0.0.1:8000/media/' + pokemon_parent[0]['photo'],
            }
        })
    current_pokemon = Pokemon.objects.get(id=int(pokemon_id))
    if current_pokemon.child.all().exists():
        pokemon.update({
            "next_evolution": {
                'pokemon_id': current_pokemon.child.all()[0].id,
                'title_ru': current_pokemon.child.all()[0].title,
                'img_url': 'http://127.0.0.1:8000/media/' + str(current_pokemon.child.all()[0].photo),
            }
        })

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity['lat'], pokemon_entity['lon'],
            pokemon['title_ru'], pokemon['img_url'])

    return render(request, "pokemon.html", context={'map': folium_map._repr_html_(),
                                                    'pokemon': pokemon})
