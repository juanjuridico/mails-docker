#!/usr/bin/env python3
"""
cli.py - Interfaz de línea de comandos para mails-docker.
"""

import argparse
import sys
from email_service import (
    generate_email,
    generate_emails,
    get_emails,
    delete_email,
    sync_emails,
    list_emails,
    deactivate_email,
)


def print_emails(emails):
    """Imprime una lista de correos."""
    if not emails:
        print("No se encontraron correos.")
        return
    for i, email in enumerate(emails, 1):
        print(f"{i}. {email['email']} (Proveedor: {email['provider']}, Dominio: {email['domain']})")
        print(f"   - Creado: {email['created_at']}")
        print(f"   - Activo: {'Sí' if email['is_active'] else 'No'}")
        print()


def print_received_emails(emails):
    """Imprime una lista de correos recibidos."""
    if not emails:
        print("No se encontraron correos recibidos.")
        return
    for i, email in enumerate(emails, 1):
        print(f"{i}. De: {email['from']}")
        print(f"   Asunto: {email['subject']}")
        print(f"   Fecha: {email['date']}")
        print(f"   Cuerpo: {email['body'][:100]}...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Generar y gestionar correos temporales con mails-docker.",
        epilog="""
Ejemplos:
  python cli.py generate --count 1
  python cli.py list
  python cli.py read usuario@gmail.com
  python cli.py delete usuario@gmail.com
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: generate
    generate_parser = subparsers.add_parser("generate", help="Genera correos temporales.")
    generate_parser.add_argument("--count", type=int, default=1, help="Número de correos. Default: 1.")
    generate_parser.add_argument("--provider", default="tempmailg", help="Proveedor. Default: tempmailg.")
    generate_parser.add_argument("--headless", action="store_false", help="Modo headless. Default: True.")

    # Comando: list
    list_parser = subparsers.add_parser("list", help="Lista correos almacenados.")
    list_parser.add_argument("--provider", default=None, help="Filtrar por proveedor.")
    list_parser.add_argument("--all", action="store_true", help="Incluir inactivos.")

    # Comando: read
    read_parser = subparsers.add_parser("read", help="Lee correos recibidos.")
    read_parser.add_argument("email", type=str, help="Dirección de correo.")
    read_parser.add_argument("--provider", default="tempmailg", help="Proveedor. Default: tempmailg.")

    # Comando: delete
    delete_parser = subparsers.add_parser("delete", help="Elimina un correo.")
    delete_parser.add_argument("email", type=str, help="Dirección de correo.")
    delete_parser.add_argument("--provider", default="tempmailg", help="Proveedor. Default: tempmailg.")

    # Comando: sync
    sync_parser = subparsers.add_parser("sync", help="Sincroniza correos.")
    sync_parser.add_argument("--provider", default="tempmailg", help="Proveedor. Default: tempmailg.")

    # Comando: deactivate
    deactivate_parser = subparsers.add_parser("deactivate", help="Marca un correo como inactivo.")
    deactivate_parser.add_argument("email", type=str, help="Dirección de correo.")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "generate":
            emails = generate_emails(args.count, args.provider, headless=args.headless)
            if emails:
                print(f"Se generaron {len(emails)} correos:")
                for email in emails:
                    print(f"  - {email}")
            else:
                print("No se pudo generar ningún correo.")

        elif args.command == "list":
            emails = list_emails(args.provider, not args.all)
            print(f"Correos {'todos' if args.all else 'activos'}:")
            print_emails(emails)

        elif args.command == "read":
            emails = get_emails(args.email, args.provider)
            print(f"Correos recibidos para {args.email}:")
            print_received_emails(emails)

        elif args.command == "delete":
            success = delete_email(args.email, args.provider)
            if success:
                print(f"Correo {args.email} eliminado.")
            else:
                print(f"No se pudo eliminar {args.email}.")

        elif args.command == "sync":
            sync_emails(args.provider)
            print(f"Sincronización completada con {args.provider}.")

        elif args.command == "deactivate":
            success = deactivate_email(args.email)
            if success:
                print(f"Correo {args.email} desactivado.")
            else:
                print(f"No se pudo desactivar {args.email}.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
