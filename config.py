htmlContent = """
<html>
	<head>
		<title>Tweets viz</title>
		<link rel="icon" href="img/tweets-viz.png"/>
		<link rel="stylesheet" href="style/main.css"/>
	</head>
	<body>
		<header>
			<h1>Tweets keywords visualization</h1>
		</header>
		<div id="params">
			<ol>
				<li>Mot clé : <strong>{motCle}</strong></li>
				<li>Nombre de tweets à récupérer : {nbTweets}</li>
				<li>Date/heure lancement du script : {timestamp}</li>
			</ol>
		</div>
		<div id="dataviz">
			<div id="hist"><img src="{hist}" alt="Histogramme"/></div>
    		<div id ="table">{wordcloud}</div>
    	</div>
    	<div id ="table">{table}</div>
	</body>
</html>
"""