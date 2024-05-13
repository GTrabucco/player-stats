$(document).ready(function () {
    $("#sdql-button").click(function () {
        var sdqlQuery = $("#sdql-input").val();
        fetchPlayerStats(sdqlQuery);
    });

    function fetchPlayerStats(sdqlQuery) {
        console.log(sdqlQuery)
        $.ajax({
            url: "fetch_player_stats",
            type: "POST",
            data: { sdql: sdqlQuery },
            success: function (response) {
                var obj = JSON.parse(response);
                var dataArray = Object.keys(obj['Player']).map(function (key) {
                    return {
                        'Player': obj['Player'][key],
                        'MP': obj['MP'][key],
                        'G': obj['G'][key],
                        'MPG': obj['MPG'][key],
                        'FGM': obj['FGM'][key],
                        'FG_ATT': obj['FG_ATT'][key],
                        'FG_PCT': obj['FG_PCT'][key],
                        '3P': obj['3P'][key],
                        '3PA': obj['3PA'][key],
                        'FG3_PCT': obj['FG3_PCT'][key],
                        'FTM': obj['FTM'][key],
                        'FT_ATT': obj['FT_ATT'][key],
                        'FT_PCT': obj['FT_PCT'][key],
                        'RPG': obj['RPG'][key],
                        'APG': obj['APG'][key],
                        'SPG': obj['SPG'][key],
                        'BPG': obj['BPG'][key],
                        'TPG': obj['TPG'][key],
                        'FPG': obj['FPG'][key],
                        'PPG': obj['PPG'][key],
                        'P+R+A': obj['P+R+A'][key],
                        'BPM': obj['BPM'][key]
                    };
                });

                $('#table').DataTable({
                    data: dataArray,
                    columns: [
                        { data: 'Player' },
                        { data: 'MP' },
                        { data: 'G' },
                        { data: 'MPG' },
                        { data: 'FGM' },
                        { data: 'FG_ATT' },
                        { data: 'FG_PCT' },
                        { data: '3P' },
                        { data: '3PA' },
                        { data: 'FG3_PCT' },
                        { data: 'FTM' },
                        { data: 'FT_ATT' },
                        { data: 'FT_PCT' },
                        { data: 'RPG' },
                        { data: 'APG' },
                        { data: 'SPG' },
                        { data: 'BPG' },
                        { data: 'TPG' },
                        { data: 'FPG' },
                        { data: 'PPG' },
                        { data: 'P+R+A' },
                        { data: 'BPM' }
                    ]
                });

                $('#table').show()
            },
            error: function () {
                alert("Error fetching player stats. Please try again later.");
            }
        });
    }
});