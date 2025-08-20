<hgroup>
<h1>Environment instructions and initial setup</h1>
<h2>Installing python, dependencies and launching server</h2>
</hgroup>
<p>
<ul>
<li>Clone the repo with <code>git clone https://github.com/gamug/medical-app.git</code></li>
<li>Set up an environment of python 3.12.4. With conda you can proceed
<code>conda create -n u3-project python==3.12.4</code>
<code>conda activate u3-project</code></li>
<li>Place the cmd in the project folder. Install the requirements using the command:
<code>pip install -r requirements.txt</code></li>
<li>Once you finish the environment setup, run the command to raise the API server
<code>uvicorn main:app --reload</code></li>
<li>Then, visit the URL http://127.0.0.1:8000/docs# to get into the swagger interface that let you interact with the backend</li>
</ul>
</p>
<hgroup>
<h1>Swagger interface and API documentation</h1>
<h2>Patient and doctor registering</h2>
</hgroup>