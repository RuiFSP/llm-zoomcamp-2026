INSTRUCTIONS = '''
Your task is to answer questions from the course participants
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
'''

PROMPT_TEMPLATE = '''
QUESTION: {question}

CONTEXT:
{context}
'''.strip()

# near top of file
try:
    import tiktoken
except Exception:
    tiktoken = None


class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        course='llm-zoomcamp',
        model='gpt-5.4-mini'
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.course = course
        self.prompt_template = prompt_template
        self.model = model
        # store last raw response and usage info
        self.last_response = None
        self.last_usage = None

    def search(self, query, num_results=5):
        boost_dict = {'content': 3.0, 'filename': 0.5}

        try:
            # call the index without the unsupported 'course' filter
            return self.index.search(
                query,
                num_results=num_results,
                boost_dict=boost_dict,
            )
        except TypeError:
            # Fallback for simple index.search(query, num_results=...)
            return self.index.search(query, num_results=num_results)
        except Exception:
            # If index validates allowed kwargs and rejects boost_dict, fall
            # back to the simplest call.
            return self.index.search(query, num_results=num_results)


    def build_context(self, search_results, max_lines=8):
        lines = []
        for doc in search_results:
            fname = doc.get('filename', '<unknown>')
            content = doc.get('content', '') or ''
            excerpt = '\n'.join(content.splitlines()[:max_lines]).strip()
            lines.append(f'File: {fname}')
            if excerpt:
                lines.append(excerpt)
            lines.append('')  # blank line between docs
        return '\n'.join(lines).strip()

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )
        
    def _get_encoder(self, model=None):
        if tiktoken:
            try:
                return tiktoken.encoding_for_model(model or self.model)
            except Exception:
                return tiktoken.get_encoding("cl100k_base")
        return None

    def estimate_tokens(self, text, model=None):
        enc = self._get_encoder(model)
        if enc:
            return len(enc.encode(text))
        # heuristic fallback ~ 4 chars per token
        return max(1, int(len(text) / 4))

    def estimate_prompt_tokens(self, query, search_results=None):
        if search_results is None:
            search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        return self.estimate_tokens(prompt)

    def estimate_and_verify_prompt_tokens(self, query, search_results=None):
        """Estimate prompt tokens using tiktoken (if available) and verify
        against provider-reported usage from the last LLM call when present.

        Returns a dict with `estimated_input_tokens` (int) and
        `provider_input_tokens` (int or None).
        """
        if search_results is None:
            search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        estimated = self.estimate_tokens(prompt)

        provider_tokens = None
        counts = self.get_last_token_counts()
        if counts and isinstance(counts, dict):
            # prefer explicit input token field from provider
            provider_tokens = int(counts.get("input_tokens") or 0)

        return {
            "estimated_input_tokens": int(estimated),
            "provider_input_tokens": provider_tokens,
        }

    def get_last_token_counts(self):
        u = self.last_usage
        if not u:
            return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

        def read(tok_name: str) -> int:
            # Try attribute access first
            val = None
            try:
                val = getattr(u, tok_name, None)
            except Exception:
                val = None
            # Then dict-style access
            if val is None and isinstance(u, dict):
                val = u.get(tok_name)
            # Normalize to int with safe fallback
            try:
                return int(val) if val is not None else 0
            except Exception:
                return 0

        input_tokens = read("input_tokens")
        output_tokens = read("output_tokens")
        total_tokens = read("total_tokens") or read("total") or (input_tokens + output_tokens)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }

    def estimate_cost(self, input_tokens, output_tokens=0, input_price_per_million=0.75, output_price_per_million=4.50):
        input_price = input_price_per_million / 1_000_000
        output_price = output_price_per_million / 1_000_000
        return input_tokens * input_price + (output_tokens or 0) * output_price

    def llm(self, prompt):
        input_messages = [
            {'role': 'developer', 'content': self.instructions},
            {'role': 'user', 'content': prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        # keep the full response object for inspection
        self.last_response = response

        # try to extract token usage from common fields
        usage = None
        try:
            # Response may be an object with attributes or a dict
            usage = getattr(response, 'usage', None)
            if usage is None and isinstance(response, dict):
                usage = response.get('usage')
            if usage is None and hasattr(response, 'meta'):
                meta = getattr(response, 'meta')
                if isinstance(meta, dict):
                    usage = meta.get('token_usage') or meta.get('usage')
                else:
                    usage = getattr(meta, 'token_usage', None) or getattr(meta, 'usage', None)
        except Exception:
            usage = None

        self.last_usage = usage

        return response.output_text

    def get_last_response(self):
        return self.last_response

    def get_last_usage(self):
        return self.last_usage

    def get_token_usage(self, response):
        if hasattr(response, 'usage'):
            return response.usage
        else:
            return None
    
    
    def rag(self, query, return_usage=False):
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        answer = self.llm(prompt)
        if return_usage:
            return answer, self.last_usage
        return answer
