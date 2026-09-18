# Prandtl-Meyer Expansion Fan & Isentropic Flow Tool

A compressible flow and supersonic aerodynamics web application built with Python and Flask.

## Features
- **Prandtl-Meyer Expansion Fan Calculator**: Computes downstream Mach number \(M_2\), Prandtl-Meyer angles (\(\nu_1, \nu_2\)), Mach wave angles (\(\mu_1, \mu_2\)), and flow property jumps (\(T_2/T_1, p_2/p_1, \rho_2/\rho_1\)).
- **Isentropic Flow Table Generator**: Generates compressible flow tables across custom Mach ranges and step intervals.
- **Gas Dynamics Formula Sheet**: Reference sheet displaying all governing analytical equations.

## Deploying to Render

### Option 1: One-Click Blueprint Deployment (Recommended)
1. Push this repository to your GitHub/GitLab account.
2. Log in to [Render](https://render.com).
3. Click **New +** -> **Blueprint**.
4. Connect this repository. Render will automatically detect `render.yaml` and configure:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click **Apply**.

### Option 2: Manual Web Service
1. In Render Dashboard, click **New +** -> **Web Service**.
2. Connect your repository.
3. Set the following settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
4. Click **Create Web Service**.

## Local Development
```bash
pip install -r requirements.txt
python app.py
```
Visit `http://localhost:5000` in your browser.
