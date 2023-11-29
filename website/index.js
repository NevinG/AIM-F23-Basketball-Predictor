yesterday = document.getElementById("yesterday");
tomorrow = document.getElementById("tomorrow");
gameContainer = document.getElementById("gameContainer");
today = document.getElementById("today");

const dateFormat = new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  });

//update to current date
let date = new Date();
let dateString = dateFormat.format(date);
today.innerHTML = dateString;



yesterday.onclick = () => {
    moveDate(-1);
    updateGameData();
}

tomorrow.onclick = () => {
    moveDate(1);
    updateGameData();
}
function moveDate(i){
    if(dateString == '10/24/2023' && i < 0)
        return;
    if(dateString == '04/14/2024' && i > 0)
        return;

    date.setDate(date.getDate() + i)
    dateString = dateFormat.format(date);
    console.log(dateString)
    if(data[dateString] == undefined)
        moveDate(i)
    today.innerHTML = dateString;
}
function updateGameData(){
    //clear game container
    gameContainer.innerHTML = "";

    //add new games
    const games = data[dateString];
    if(!games)
        return;
    for(let i = 0; i < games.length; i++){
        let game = document.createElement('div');
        game.className = "game";

        game.innerHTML = `${games[i]["homeTeam"]} ${games[i]["prediction"] !== "" ? `(${games[i]["prediction"]})`: ""} ${games[i]["homeTeamPoints"]} - ${games[i]["awayTeamPoints"]} ${games[i]["prediction"] !== "" ? `(${Math.round( (1 - games[i]["prediction"]) * 100) / 100})`: ""} ${games[i]["awayTeam"]}`
        gameContainer.appendChild(game);

        //calculate if prediction was correct and change background
        if(games[i]["prediction"] !== "" && games[i]["homeTeamPoints"] !== ""){
            if(games[i]["homeTeamPoints"] > games[i]["awayTeamPoints"] && games[i]["prediction"] >= .5){
                game.style.backgroundColor = "#77c877"
            } else if(games[i]["homeTeamPoints"] < games[i]["awayTeamPoints"] && games[i]["prediction"] < .5){
                game.style.backgroundColor = "#77c877"
            } else{
                game.style.backgroundColor = "#d84747"
            }
        }else{
            game.style.backgroundColor = "#d4d4d4"
        }
        
    }
}

updateGameData();