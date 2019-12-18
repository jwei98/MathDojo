# Zip the required files and upload using aws-cli.
zip lambda_exports/app.zip app.py
aws lambda update-function-code --function-name MathDojo \
	--zip-file fileb://lambda_exports/app.zip
