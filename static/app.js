'use strict';

const KEY = 'apiKey=f513086da55b4ffbbb711aa83cdddd70';
const RECIPE_URL = 'https://api.spoonacular.com/recipes';

const $res_area = $("#res");
const $GO_button = $("#GO");
const $search_form = $("#search_form");
const $rand_sug = $("#rand_sug");
const $save_area = $("#save_div");
const $liked_recipes = $("#liked_recipe_list");


$res_area.on("click", function (evt) {
    evt.preventDefault();
    let target = evt.target;
    console.log(target.id);
    getRecipeDetails(target.id);
  });

$save_area.on("click", function (evt) {
    let target = evt.target;
    console.log(target.id);
    window.location.href=`/save_recipe/${target.id}`;
  });

async function getRecipeDetails(id) {
    let ingredients_list = [];
    const response = await axios.get(
        `${RECIPE_URL}/${id}/information?${KEY}`
        );
    $save_area.append(`<a href="/save_recipe/${id}" id="${id}"><b>SAVE THIS RECIPE !</b></a><br>`);
    ingredients_list = response.data.extendedIngredients;
    console.log(response.data);
    $res_area.empty();
    $res_area.append(`<div>`);
    $res_area.append(`<h2>${response.data.title}</h2>`);
    
    $res_area.append(`</div>`);
    $res_area.append(`<p> </p>`);
    $res_area.append(`<p><b>CATEGORIES</b> : ${response.data.cuisines}</p>`);
    $res_area.append(`<p><b>SUITABLE FOR</b> : ${response.data.dishTypes}</p>`);
    $res_area.append(`<p><b>DIETS</b> : ${response.data.diets}</p>`);
    $res_area.append(`<p><b>READY IN</b> : ${response.data.readyInMinutes} minutes</p>`);
    $res_area.append(`<p><b>MAKES</b> : ${response.data.servings} servings</p>`);
   
    $res_area.append(`<img src="${response.data.image}"><br>`);
    $res_area.append(`<h3>SUMMARY : </h3>`);
    $res_area.append(`<p>${response.data.summary}</p>`);
    $res_area.append(`<h3>DIRECTIONS : </h3>`);
    $res_area.append(`<p>${response.data.instructions}</p>`);
    $res_area.append(`<h3>INGREDIENTS : </h3>`);
    $res_area.append(`<ul>`);
    for (let i = 0; i < ingredients_list.length; i++) {
        $res_area.append(`<li>${ingredients_list[i].original}</li>`);
    }
    $res_area.append(`</ul>`);
    $res_area.append(`<br>`);
    $res_area.append(`<a href="${response.data.sourceUrl}" target="_blank">Visit source</a>`);
    
    
    }
    

$GO_button.on("click", function (event) {
        event.preventDefault();
        $res_area.empty();
        let search_term = $('#search_form input[name="search_term"]').val();
        console.log(search_term);
        getRecipe(search_term);
    });



async function getRecipe(query, l=100) {
    let loop_legth = 0;
    let id_array = [];
    let length = `number=${l}`;
    let q = `query=${query}`;

    const response = await axios.get(
        `${RECIPE_URL}/complexSearch?${KEY}&${q}&${length}`
        );
    
    if (response.data.number > response.data.totalResults) {
        loop_legth = response.data.totalResults;
    } else {
        loop_legth = response.data.number;
    }

    for (let i = 0; i < loop_legth; i++) {
        console.log(response.data.results[i].title);
        $res_area.append(`<p
                            class="link"
                            id="${response.data.results[i].id}">
                            ${response.data.results[i].title}</p>`);
        console.log(response.data.results[i].id);    
        id_array.push(response.data.results[i].id);
    }
    return id_array;
}


async function getRnadRecipe() {
    const response = await axios.get(
        `${RECIPE_URL}/random?${KEY}&number=1`
        );   
    $rand_sug.append(`<p
                        class="link"
                        id="${response.data.recipes[0].id}">
                        May I suggest you try, 
                        ${response.data.recipes[0].title}</p>`);
}



$rand_sug.on("click", function (evt) {
    evt.preventDefault();
    let target = evt.target;
    console.log(target.id);
    getRecipeDetails(target.id);
  });

function populateFavorites() {
    let this_id = ''
    let liked_recipe_ids = [];
    $liked_recipes.children().each(async function () {
        this_id = $(this).attr('id');
        liked_recipe_ids.push(this_id);
        $(this).append(` <div class="card-body" >
                        <p class="card-text">
                        ${await getRecipeTitle(this_id)}
                        </p>
                        </div>`);         
    });
    console.log(liked_recipe_ids)
    return liked_recipe_ids;
}

async function getRecipeTitle(id) {
    let title = '';
    const response = await axios.get(
        `${RECIPE_URL}/${id}/information?${KEY}`
        );
    title = response.data.title;
    return title;
}
    



populateFavorites();
getRnadRecipe();