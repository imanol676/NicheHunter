import os

FILE_PATH = r"c:\Users\imano\OneDrive\Escritorio\proyectos\painpoint_scraper\frontend\src\app\(marketing)\page.tsx"

with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    'Iniciar Sesión': 'Sign In',
    'Empezar Gratis': 'Get Started for Free',
    'Ir al Dashboard': 'Go to Dashboard',
    'Motor de IA v1.0 Activo': 'AI Engine v1.0 Active',
    'Descubrir Startups': 'Discover hidden',
    'ocultas en internet': 'Startups on the internet',
    'Navega en oportunidades de negocio que nadie más ve. Nuestra IA escanea miles de quejas reales en Reddit y te entrega ideas de SaaS validadas antes de que escribas una sola línea de código.': 'Navigate business opportunities no one else sees. Our AI scans thousands of real complaints on Reddit and delivers validated SaaS ideas before you write a single line of code.',
    'Infiltrar un Nicho': 'Infiltrate a Niche',
    'Acceder a la Terminal': 'Access Terminal',
    'Deja de adivinar qué construir': 'Stop guessing what to build',
    'Horas perdidas buscando': 'Hours wasted searching',
    'Leer miles de hilos en Reddit para encontrar un problema real consume días. Nuestra IA lo hace en segundos.': 'Reading thousands of Reddit threads to find a real problem takes days. Our AI does it in seconds.',
    'Construir sin demanda': 'Building without demand',
    'El 90% de las startups mueren porque resuelven problemas que no existen. Nosotros partimos del dolor real.': '90% of startups die because they solve problems that do not exist. We start from real pain.',
    'Falta de claridad': 'Lack of clarity',
    'Encontrar una queja es fácil, convertirla en un modelo de negocio rentable (SaaS) es difícil. Nosotros te damos el plan.': 'Finding a complaint is easy, converting it into a profitable business model (SaaS) is hard. We give you the plan.',
    '¿Cómo funciona el motor?': 'How does the engine work?',
    'Defines el Objetivo': 'Define the Objective',
    'Ingresas un nicho o audiencia específica. (Ej: Editores de video freelance).': 'You enter a specific niche or audience. (Ex: Freelance video editors).',
    'Extracción Profunda': 'Deep Extraction',
    'Nuestros spiders navegan subreddits específicos buscando publicaciones tóxicas, quejas y frustraciones repetitivas.': 'Our spiders navigate specific subreddits looking for toxic posts, complaints, and repetitive frustrations.',
    'Clustering Vectorial': 'Vector Clustering',
    'Usamos Embeddings de OpenAI y HDBSCAN para agrupar quejas similares y descubrir patrones ocultos.': 'We use OpenAI Embeddings and HDBSCAN to group similar complaints and discover hidden patterns.',
    'Oportunidad de Negocio': 'Business Opportunity',
    'Azure GPT-4o analiza los grupos matemáticos y te devuelve un pitch de startup con modelo de monetización y solución.': 'Azure GPT-4o analyzes the mathematical groups and returns a startup pitch with a monetization model and solution.'
}

for es, en in replacements.items():
    content = content.replace(es, en)

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Translation completed successfully.")
