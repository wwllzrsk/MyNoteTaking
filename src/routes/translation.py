import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from openai import OpenAI, OpenAIError

translation_bp = Blueprint('translation', __name__)
ROOT_DIR = Path(__file__).resolve().parents[2]
PROMPT_PATH = ROOT_DIR / 'prompts' / 'translate_prompt.md'
MODEL = 'nvidia/nemotron-3-super-120b-a12b:free'


@translation_bp.route('/translate', methods=['POST'])
def translate():
    """Translate note text and return the result as JSON."""
    if not request.is_json:
        return jsonify({'error': 'Request body must be JSON'}), 400

    data = request.get_json()
    text = data.get('text') if isinstance(data, dict) else None
    target_language = data.get('target_language') if isinstance(data, dict) else None
    if not isinstance(text, str) or not text.strip():
        return jsonify({'error': 'Text is required'}), 400
    if not isinstance(target_language, str) or not target_language.strip():
        return jsonify({'error': 'Target language is required'}), 400

    load_dotenv(ROOT_DIR / '.env')
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        return jsonify({'error': 'Translation service is not configured'}), 503

    try:
        prompt_template = PROMPT_PATH.read_text(encoding='utf-8')
    except OSError:
        return jsonify({'error': 'Translation prompt file is unavailable'}), 500

    system_prompt = prompt_template.replace(
        '{{target_language}}', target_language.strip()
    )
    client = OpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=api_key,
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': text},
            ],
            response_format={'type': 'json_object'},
        )
    except OpenAIError:
        return jsonify({'error': 'Translation service request failed'}), 502

    if not response.choices:
        return jsonify({'error': 'Translation service returned no result'}), 502

    result_content = response.choices[0].message.content
    try:
        result = json.loads(result_content) if result_content else None
    except json.JSONDecodeError:
        result = None

    translated_text = result.get('translation') if isinstance(result, dict) else None
    if not isinstance(translated_text, str):
        return jsonify({'error': 'Translation service returned an invalid JSON result'}), 502

    return jsonify({
        'source_text': text,
        'target_language': target_language.strip(),
        'translated_text': translated_text,
    })
