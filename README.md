cd ~/my_scripts/impostor
git init
git add .
git config --global user.email "espinaitor@gmail.com"
git config --global user.name "espinaitor"
git commit -m "Primera versión del Impostor"
git branch -M main
git remote add origin https://github.com/espinaitor/impostor-app.git
git push -u origin main
    
