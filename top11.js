import { GoogleGenerativeAI } from "@google/generative-ai";
import fetch from "node-fetch";

async function fetchSquads() {
    const apiUrl = "http://127.0.0.1:8000/get_squads/";
    const requestBody = {
        team1: "Chennai Super Kings",
        team2: "Mumbai Indians"
    };

    try {
        const response = await fetch(apiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestBody)
        });
        
        const squadData = await response.json();
        console.log("Squad Data:", squadData);
        
        const geminiResponse = await sendToGemini(squadData);
        console.log("Extracted Team:", geminiResponse);
    } catch (error) {
        console.error("Error fetching squads:", error);
    }
}

async function sendToGemini(squadData) {
    const genAI = new GoogleGenerativeAI("");  // Replace with your actual API key
    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

    const prompt = `Please help me create an optimal Dream11 fantasy cricket team from the following player squads:

                    ${JSON.stringify(squadData)}

                    Requirements:
                    1. Select exactly 11 players total
                    2. Maximum 6 players from any single team
                    3. Must include players for these roles:
                    - Wicketkeepers (WK)
                    - Batsmen (BAT)
                    - All-rounders (AR)
                    - Bowlers (BOWL)

                    Please provide your selection in this specific format:
                    wk_players = [...]
                    bat_players = [...]
                    ar_players = [...]
                    bowl_players = [...]

                    Consider the following when making selections:
                    - Recent form and performance
                    - Player strengths against the opposition
                    - Pitch conditions and match venue
                    - Players likely to contribute maximum fantasy points
                    - Balance between consistent performers and high-potential players`;

    try {
        const result = await model.generateContent(prompt);
        const responseText = result.response.text();
        
        return extractPlayers(responseText);
    } catch (error) {
        console.error("Error sending data to Gemini API:", error);
    }
}

function extractPlayers(responseText) {
    try {
        const wk_players = responseText.match(/wk_players\s*=\s*\[([^\]]+)\]/)[1].split(",").map(player => player.trim().replace(/['"]/g, ""));
        const bat_players = responseText.match(/bat_players\s*=\s*\[([^\]]+)\]/)[1].split(",").map(player => player.trim().replace(/['"]/g, ""));
        const ar_players = responseText.match(/ar_players\s*=\s*\[([^\]]+)\]/)[1].split(",").map(player => player.trim().replace(/['"]/g, ""));
        const bowl_players = responseText.match(/bowl_players\s*=\s*\[([^\]]+)\]/)[1].split(",").map(player => player.trim().replace(/['"]/g, ""));

        return { wk_players, bat_players, ar_players, bowl_players };
    } catch (error) {
        console.error("Error extracting players:", error);
        return { wk_players: [], bat_players: [], ar_players: [], bowl_players: [] };
    }
}

fetchSquads();
