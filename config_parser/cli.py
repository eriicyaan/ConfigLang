import sys
import json
import argparse
import lark


try:
    from .parser import create_parser
    from .transformer import ConfigTransformer
except ImportError:
    from parser import create_parser
    from transformer import ConfigTransformer

def main():
    parser = argparse.ArgumentParser(description='Convert config to JSON')
    parser.add_argument('-o', '--output', required=True, help='Output JSON file path')
    args = parser.parse_args()

    if sys.stdin.encoding != 'utf-8':
        input_text = sys.stdin.buffer.read().decode('utf-8')
    else:
        input_text = sys.stdin.read()

    transformer = ConfigTransformer()

    try:
        lark_parser = create_parser(transformer)
        tree = lark_parser.parse(input_text)

        result = [item for item in tree if item is not None]

        # Записываем с явным указанием кодировки UTF-8 и отключением экранирования
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    except lark.exceptions.LarkError as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Runtime error: {str(e)}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()