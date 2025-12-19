# 🔐 Configuration des Secrets GitHub

## 📝 Secrets à Configurer

Suivez ces étapes pour configurer les secrets sur GitHub Actions :

### **Accès aux Secrets**

1. Allez sur votre repository : https://github.com/Moutacdie2000/containers-cicd-challenge
2. Cliquez sur **Settings** (en haut à droite)
3. Dans le menu gauche, sélectionnez **Secrets and variables** → **Actions**
4. Cliquez sur **New repository secret**

### **Secrets à Ajouter**

#### 1️⃣ `DB_PASSWORD` (Optionnel - Dev)

```
Name: DB_PASSWORD
Value: postgres
Description: PostgreSQL password for CI/CD tests
```

**Utilisation** : Tests d'intégration Docker Compose

---

#### 2️⃣ `GITHUB_TOKEN` (Automatique ✅)

**Vous N'AVEZ RIEN À FAIRE** - GitHub le fournit automatiquement

```yaml
# Déjà utilisé dans le workflow
password: ${{ secrets.GITHUB_TOKEN }}
```

---

### **Secrets Optionnels (Production)**

Si vous déployez en production, ajoutez :

#### 3️⃣ `DOCKERHUB_USERNAME` (Optionnel)

```
Name: DOCKERHUB_USERNAME
Value: votre_username_docker
```

#### 4️⃣ `DOCKERHUB_TOKEN` (Optionnel)

```
Name: DOCKERHUB_TOKEN
Value: votre_token_docker
```

#### 5️⃣ `SLACK_WEBHOOK_URL` (Optionnel)

```
Name: SLACK_WEBHOOK_URL
Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## ✅ Pour Votre Cas (Développement)

**Minimum requis :** Rien ! 

Le workflow fonctionne déjà avec :
- `GITHUB_TOKEN` (automatique)
- Variables hardcodées pour tests

---

## 🔒 Bonnes Pratiques

### ✅ À faire

```yaml
# Utiliser les secrets
password: ${{ secrets.DB_PASSWORD }}
```

### ❌ À éviter

```yaml
# Ne JAMAIS mettre en dur
password: "my-super-secret"
```

---

## 📖 Référence : Variables dans le Workflow

Les secrets sont utilisés ici :

```yaml
# Dans ci.yml - Job: docker-compose-test

- name: Create .env file for docker-compose
  run: |
    cd docker
    cat > .env << EOF
    DB_USER=postgres
    DB_PASSWORD=${{ secrets.DB_PASSWORD || 'postgres' }}  # ← Secret optionnel
    DB_NAME=fastapi_db
    EOF
```

**Explication** :
- Si `DB_PASSWORD` secret existe → l'utiliser
- Sinon → utiliser la valeur par défaut `'postgres'`

---

## 🚀 Après Configuration

Une fois les secrets ajoutés :

1. Poussez du code vers `main` ou `develop`
2. Le workflow se déclenche automatiquement
3. Les secrets sont disponibles dans les jobs

```bash
git add .
git commit -m "Configure GitHub secrets"
git push origin main
```

---

## 🔍 Vérifier les Secrets

Dans **Settings** → **Secrets and variables** → **Actions**, vous verrez :

```
✅ DB_PASSWORD
✅ GITHUB_TOKEN (auto)
```

Les valeurs ne sont jamais visibles après création.

---

## ⚠️ Important

- Les secrets ne s'affichent **JAMAIS** dans les logs
- Ils sont sécurisés par GitHub
- Chaque secret est lié à UN repository
- Ils expirent pas

---

**C'est prêt ! Votre workflow est configuré correctement.** 🎉
