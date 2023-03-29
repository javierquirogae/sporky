const KEY = 'f513086da55b4ffbbb711aa83cdddd70'


async function getResponse() {
    
    const response = await axios.get(
        `https://api.spoonacular.com/recipes/complexSearch?apiKey=${KEY}&query=pasta&maxFat=25&number=2`
        );
    
    console.log(response.data);
}