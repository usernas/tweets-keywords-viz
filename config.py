htmlContent = """
<html>
	<head>
		<title>Tweets viz</title>
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
			<div id="hist">{hist}</div>
    		<div id ="table">{table}</div>
    	</div>
	</body>
</html>
"""