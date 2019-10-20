import folium

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

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
    pokemons = Pokemon.objects.values()
    pokemon_entities = PokemonEntity.objects.values()

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    pokemon_dict = dict([(key, value) for (key, value) in zip([pokemon['id'] for pokemon in pokemons],
                                                              [pokemon for pokemon in pokemons])])

    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity['lat'], pokemon_entity['lon'],
            pokemon_dict[pokemon_entity['pokemon_id']]['title'],
            request.build_absolute_uri('/media/') + pokemon_dict[pokemon_entity['pokemon_id']]['photo'])

    pokemons_on_page = []
    for pokemon in pokemons:
        pokemons_on_page.append({
            'pokemon_id': pokemon['id'],
            'title_ru': pokemon['title'],
            'img_url': request.build_absolute_uri('/media/') + pokemon['photo'],
        })

    return render(request, "mainpage.html", context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        current_pokemon = Pokemon.objects.get(id=int(pokemon_id))
    except ObjectDoesNotExist:
        print("Pokemon doesn't exist.")

    pokemons_for_show = PokemonEntity.objects.filter(pokemon_id=int(pokemon_id))

    pokemon = {
        'pokemon_id': current_pokemon.id,
        'title_ru': current_pokemon.title,
        'img_url': request.build_absolute_uri('/media/') + str(current_pokemon.photo),
        'title_en': current_pokemon.title_en,
        'title_jp': current_pokemon.title_jp,
        'description': current_pokemon.description,
    }

    if not (current_pokemon.evolution_from is None):
        pokemon_parent = current_pokemon.evolution_from

        pokemon.update({
            "previous_evolution": {
                'pokemon_id': pokemon_parent.id,
                'title_ru': pokemon_parent.title,
                'img_url': request.build_absolute_uri('/media/') + str(pokemon_parent.photo),
            }
        })

    if current_pokemon.children.exists():
        next_pokemon = current_pokemon.children.all()[0]
        pokemon.update({
            "next_evolution": {
                'pokemon_id': next_pokemon.id,
                'title_ru': next_pokemon.title,
                'img_url': request.build_absolute_uri('/media/') + str(next_pokemon.photo),
            }
        })

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_for_show in pokemons_for_show:
        add_pokemon(
            folium_map, pokemon_for_show.lat, pokemon_for_show.lon,
            pokemon['title_ru'], pokemon['img_url'])

    return render(request, "pokemon.html", context={'map': folium_map._repr_html_(),
                                                    'pokemon': pokemon})
