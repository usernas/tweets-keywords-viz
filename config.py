htmlContent = """
<html>
	<head>
		<title>Tweets viz</title>
		<link rel="icon" href="img/tweets-viz.png"/>
		<link rel="stylesheet" href="style/main.css"/>
	</head>
	<body>
		<header>
			<h1>Tweets Keywords Visualization</h1>
		</header>
		<div id="params">
			<ol>
				<li>Mot clé : <strong class="red">{motCle}</strong></li>
				<li>Nombre de tweets à récupérer : <strong>{nbTweets}</strong></li>
				<li>Date/heure lancement du script : <strong>{timestamp}</strong></li>
			</ol>
		</div>
		<div id="dataviz">
			<div id="hist" class="inline-bloc"><img src="{hist}" alt="Histogramme"/></div>
    		<div id ="wordcloud" class="inline-bloc"><img src="{wordcloud}" alt="Wordcloud"/></div>
    	</div>
    	<div>{table}</div>
	</body>
</html>
"""