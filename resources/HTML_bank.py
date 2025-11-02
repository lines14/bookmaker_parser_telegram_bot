class HTMLBank:
    def get_HTML_from_template(competition_type, tournament_name, game_models_matrix):
        head = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Template</title>
    <style>
        @font-face {{
            font-family: "CeraPro-Black";
            src: url("./fonts/CeraPro-Black.woff");
        }}
        @font-face {{
            font-family: "CeraPro-BlackItalic";
            src: url("./fonts/CeraPro-BlackItalic.woff");
        }}
        @font-face {{
            font-family: "CeraPro-Bold";
            src: url("./fonts/CeraPro-Bold.woff");
        }}
        @font-face {{
            font-family: "CeraPro-BoldItalic";
            src: url("./fonts/CeraPro-BoldItalic.woff");
        }}
        @font-face {{
            font-family: "CeraPro-Italic";
            src: url("./fonts/CeraPro-Italic.woff");
        }}
        @font-face {{
            font-family: "CeraPro-Light";
            src: url("./fonts/CeraPro-Light.woff");
        }}
        @font-face {{
            font-family: "CeraPro-LightItalic";
            src: url("./fonts/CeraPro-LightItalic.woff");
        }}
        @font-face {{
            font-family: "CeraPro-Medium";
            src: url("./fonts/CeraPro-Medium.woff");
        }}
        @font-face {{
            font-family: "CeraPro-MediumItalic";
            src: url("./fonts/CeraPro-MediumItalic.woff");
        }}
        @font-face {{
            font-family: "CeraPro-Regular";
            src: url("./fonts/CeraPro-Regular.woff");
        }}
        @font-face {{
            font-family: "CeraPro-Thin";
            src: url("./fonts/CeraPro-Thin.woff");
        }}
        @font-face {{
            font-family: "CeraPro-ThinItalic";
            src: url("./fonts/CeraPro-ThinItalic.woff");
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'CeraPro-Bold'; 
            font-size: 60px;
            max-width: 1080px;
            margin: 0 auto;
            color: rgb(255, 255, 255);
            overflow-x: hidden;
            overflow-y: hidden;
        }}
        .background {{
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 1080px;
            height: 1920px;
            background-image: url('./assets/Back-1080x1920.jpg');
            padding-top: 156px;
        }}
        .stripe {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-top: 8px;
            width: 1080px;
            height: 305px;
            background-image: url('./assets/lenta.png');
        }}
        .small-title {{
            color: #FFF;
            text-align: center;
            font-family: 'CeraPro-Bold';
            font-size: 45.252px;
            font-style: normal;
            font-weight: 400;
            line-height: 41.328px; /* 91.329% */
            text-transform: uppercase;
        }}
        .big-title {{
            color: #FFF;
            text-align: center;
            font-family: 'CeraPro-Bold';
            font-size: 145.953px;
            font-style: normal;
            font-weight: 900;
            line-height: 176.941px; /* 121.231% */
            letter-spacing: -2.743px;
            text-transform: uppercase;
        }}
        .date {{
            color: #E80024;
            text-align: center;
            font-family: 'CeraPro-Bold';
            font-size: 45.833px;
            font-style: normal;
            font-weight: 900;
            line-height: 62.463px; /* 136.284% */
            text-transform: uppercase;
        }}
        .table {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-direction: column;
            width: 918px;
        }}
        .row {{
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
            width: 918px;
            height: 124px;
            margin-bottom: 16px;
        }}
        .middle-cell {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            width: 187px;
            height: 124px;
        }}
        .cell {{
            display: flex;
            flex-direction: row;
            align-items: center;
            border-radius: 30px;
            width: 310px;
            height: 124px;
            background-color: #272727;
        }}
        .mirror-cell {{
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-end;
            border-radius: 30px;
            width: 310px;
            height: 124px;
            background-color: #272727;
        }}
        .image {{
            margin-left: 20px;
            width: 70px;
            height: 70px;
            border-radius: 20px;
        }}
        .info {{
            margin-left: 20px;
            margin-right: 20px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: center;
            height: 124px;
            width: 200px
        }}
        .mirror-image {{
            margin-left: 0;
            margin-right: 20px;
            width: 70px;
            height: 70px;
            border-radius: 20px;
        }}
        .mirror-info {{
            margin-right: 20px;
            margin-right: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 124px;
            width: 200px;
            order: -1;
            align-items: flex-end;
            text-align: right;
        }}
        .name {{
            color: #FFF;
            font-family: 'CeraPro-Bold';
            font-size: 29.458px;
            font-style: normal;
            font-weight: 700;
            letter-spacing: -1.2px;
            text-transform: uppercase;
        }}
        .rate {{
            width: 100%;
            color: #FFF;
            font-family: 'CeraPro-Bold';
            font-size: 62.802px;
            font-style: normal;
            font-weight: 900;
            text-transform: uppercase;
        }}
        .middle-rate {{
            width: 100%;
            background-color: #272727;
            border-radius: 20px;
            color: #E80024;
            text-align: center;
            font-family: 'CeraPro-Bold';
            font-size: 60.982px;
            font-style: normal;
            font-weight: 900;
            text-transform: uppercase;
        }}
        .time {{
            color: #FFF;
            text-align: center;
            font-family: 'CeraPro-Bold';
            font-size: 36.613px;
            font-style: normal;
            font-weight: 700;
            line-height: 46.74px; /* 127.66% */
            text-transform: uppercase;
        }}
    </style>
</head>
<body>
    <div class="background">
        <img class="logo" src="./assets/logo.svg" width="191" height="46">
        <div class="stripe">
            <div class="small-title">{competition_type}</div>
            <div class="big-title">{tournament_name}</div>
        </div>'''

        body = ''
        for same_date_game_models in game_models_matrix:
            block = f'''<div class="date">{same_date_game_models[0].date}</div>
            <div class="table">'''

            body+=block

            for game in same_date_game_models:
                section = f'''<div class="row">
                    <div class="cell">
                        <img class="image" src="https://{game.teams.firstTeam.logo}" alt="First team logo">
                        <div class="info">
                            <div class="name">{game.teams.firstTeam.name}</div>
                            <div class="rate">{game.teams.firstTeam.rate}</div>
                        </div>
                    </div>
                    <div class="middle-cell">
                        <div class="time">{game.time}</div>
                        <div class="middle-rate">{game.teams.draw.rate}</div>
                    </div>
                    <div class="mirror-cell">
                        <img class="mirror-image" src="https://{game.teams.secondTeam.logo}" alt="Second team logo">
                        <div class="mirror-info">
                            <div class="name">{game.teams.secondTeam.name}</div>
                            <div class="rate">{game.teams.secondTeam.rate}</div>
                        </div>
                    </div>
                </div>'''

                body+=section

        return head+body+'</div></div></body></html>'