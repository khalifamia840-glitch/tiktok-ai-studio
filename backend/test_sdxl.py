# -*- coding: utf-8 -*-
"""Test rapido de Stable Diffusion XL con el token de Hugging Face"""
import asyncio, os, sys
import aiohttp
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN', '')
SDXL_API = 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0'

async def test_sdxl():
    print(f'Token: {HF_TOKEN[:10]}...')
    print('Probando conexion con SDXL...')
    headers = {'Authorization': f'Bearer {HF_TOKEN}', 'Content-Type': 'application/json'}
    payload = {'inputs': 'luxury sports car on highway, cinematic, 4k, vertical',
               'parameters': {'width': 512, 'height': 896, 'num_inference_steps': 20}}
    async with aiohttp.ClientSession() as s:
        async with s.post(SDXL_API, headers=headers, json=payload,
                          timeout=aiohttp.ClientTimeout(total=90)) as r:
            print(f'Status: {r.status}')
            if r.status == 200:
                data = await r.read()
                with open('test_sdxl.jpg', 'wb') as f:
                    f.write(data)
                print(f'EXITO! Imagen generada: {len(data)} bytes -> test_sdxl.jpg')
            elif r.status == 503:
                text = await r.text()
                print(f'Modelo cargando (normal la primera vez): {text[:200]}')
                print('Espera 30 segundos y vuelve a intentar')
            elif r.status == 401:
                print('ERROR: Token invalido o sin permisos')
            else:
                text = await r.text()
                print(f'ERROR {r.status}: {text[:300]}')

asyncio.run(test_sdxl())