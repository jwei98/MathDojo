# Note this is more for documentation since publish-layer-version doesn't work.
zip -r ./lambda_exports/lambda_layer.zip \
	~/.envs/MathDojo/lib/python3.8/site-packages/
aws lambda publish-layer-version --layer-name MathDojo \
	--description "Dependencies for MathDojo" \
	--compatible-runtimes python3.8 \
	--zip-file fileb://lambda_exports/lambda_layer.zip
