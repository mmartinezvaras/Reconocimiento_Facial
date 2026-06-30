import { Component, signal } from '@angular/core';

@Component({
  selector: 'app-root',
  imports: [],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly fileName = signal('');
  protected readonly headers = signal<string[]>([]);
  protected readonly rows = signal<string[][]>([]);
  protected readonly totalRows = signal(0);
  protected readonly error = signal('');

  protected async openCsv(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];

    if (!file) return;

    this.error.set('');

    try {
      const contents = (await file.text()).replace(/^\uFEFF/, '');
      const parsed = this.parseCsv(contents);

      if (parsed.length === 0) {
        throw new Error('El archivo está vacío.');
      }

      this.fileName.set(file.name);
      this.headers.set(parsed[0]);
      this.rows.set(parsed.slice(1, 1001));
      this.totalRows.set(Math.max(parsed.length - 1, 0));
    } catch {
      this.fileName.set('');
      this.headers.set([]);
      this.rows.set([]);
      this.totalRows.set(0);
      this.error.set('No se pudo leer el archivo. Comprueba que sea un CSV válido.');
    } finally {
      input.value = '';
    }
  }

  private parseCsv(contents: string): string[][] {
    const delimiter = this.detectDelimiter(contents);
    const result: string[][] = [];
    let row: string[] = [];
    let value = '';
    let insideQuotes = false;

    for (let index = 0; index < contents.length; index++) {
      const character = contents[index];

      if (character === '"') {
        if (insideQuotes && contents[index + 1] === '"') {
          value += '"';
          index++;
        } else {
          insideQuotes = !insideQuotes;
        }
      } else if (character === delimiter && !insideQuotes) {
        row.push(value.trim());
        value = '';
      } else if ((character === '\n' || character === '\r') && !insideQuotes) {
        if (character === '\r' && contents[index + 1] === '\n') index++;
        row.push(value.trim());
        if (row.some((cell) => cell.length > 0)) result.push(row);
        row = [];
        value = '';
      } else {
        value += character;
      }
    }

    row.push(value.trim());
    if (row.some((cell) => cell.length > 0)) result.push(row);

    return result;
  }

  private detectDelimiter(contents: string): string {
    const firstLine = contents.split(/\r?\n/, 1)[0] ?? '';
    const candidates = [',', ';', '\t'];
    return candidates.reduce((best, candidate) =>
      firstLine.split(candidate).length > firstLine.split(best).length ? candidate : best,
    );
  }
}
