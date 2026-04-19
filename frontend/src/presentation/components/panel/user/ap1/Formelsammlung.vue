<template>
  <div>
    <h2 class="text-xl font-bold text-[var(--color-text-primary)] mb-2">Formelsammlung &amp; Referenz</h2>
    <p class="text-[var(--color-text-secondary)] mb-6">Alle wichtigen Formeln und Tabellen fuer die AP1 auf einen Blick</p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- OSI Model -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
        <div class="text-sm font-bold text-primary-600 mb-3">OSI-Modell</div>
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-[var(--color-border)]">
              <th class="text-left py-1 text-[var(--color-text-secondary)]">Nr</th>
              <th class="text-left py-1 text-[var(--color-text-secondary)]">Name</th>
              <th class="text-left py-1 text-[var(--color-text-secondary)]">Beispiele</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in osiLayers" :key="l.nr" class="border-b border-[var(--color-border)]">
              <td class="py-1.5 font-bold text-primary-600">{{ l.nr }}</td>
              <td class="py-1.5 text-[var(--color-text-primary)]">{{ l.name }}</td>
              <td class="py-1.5 text-[var(--color-text-secondary)] text-xs">{{ l.examples }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Subnetting -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
        <div class="text-sm font-bold text-primary-600 mb-3">Subnetting-Tabelle</div>
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-[var(--color-border)]">
              <th class="text-left py-1 text-[var(--color-text-secondary)]">CIDR</th>
              <th class="text-left py-1 text-[var(--color-text-secondary)]">Maske</th>
              <th class="text-left py-1 text-[var(--color-text-secondary)]">Hosts</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in subnetTable" :key="s.cidr" class="border-b border-[var(--color-border)]">
              <td class="py-1 font-mono text-primary-600">/{{ s.cidr }}</td>
              <td class="py-1 font-mono text-[var(--color-text-primary)] text-xs">{{ s.mask }}</td>
              <td class="py-1 text-[var(--color-text-secondary)]">{{ s.hosts }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Private IP Ranges -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
        <div class="text-sm font-bold text-primary-600 mb-3">Private IP-Bereiche</div>
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-[var(--color-border)]">
              <th class="text-left py-1 text-[var(--color-text-secondary)]">Klasse</th>
              <th class="text-left py-1 text-[var(--color-text-secondary)]">Bereich</th>
              <th class="text-left py-1 text-[var(--color-text-secondary)]">CIDR</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-[var(--color-border)]"><td class="py-1 font-bold">A</td><td class="py-1 font-mono text-xs">10.0.0.0 - 10.255.255.255</td><td class="py-1 font-mono">/8</td></tr>
            <tr class="border-b border-[var(--color-border)]"><td class="py-1 font-bold">B</td><td class="py-1 font-mono text-xs">172.16.0.0 - 172.31.255.255</td><td class="py-1 font-mono">/12</td></tr>
            <tr><td class="py-1 font-bold">C</td><td class="py-1 font-mono text-xs">192.168.0.0 - 192.168.255.255</td><td class="py-1 font-mono">/16</td></tr>
          </tbody>
        </table>
      </div>

      <!-- SQL Commands -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
        <div class="text-sm font-bold text-primary-600 mb-3">SQL Befehle</div>
        <div class="space-y-2 text-sm">
          <div class="p-2 bg-[var(--color-surface-secondary)] rounded font-mono text-xs">
            <span class="text-primary-600 font-bold">SELECT</span> spalte <span class="text-primary-600 font-bold">FROM</span> tabelle <span class="text-primary-600 font-bold">WHERE</span> bedingung;
          </div>
          <div class="p-2 bg-[var(--color-surface-secondary)] rounded font-mono text-xs">
            <span class="text-primary-600 font-bold">INSERT INTO</span> tabelle (sp1, sp2) <span class="text-primary-600 font-bold">VALUES</span> (w1, w2);
          </div>
          <div class="p-2 bg-[var(--color-surface-secondary)] rounded font-mono text-xs">
            <span class="text-primary-600 font-bold">UPDATE</span> tabelle <span class="text-primary-600 font-bold">SET</span> spalte = wert <span class="text-primary-600 font-bold">WHERE</span> bedingung;
          </div>
          <div class="p-2 bg-[var(--color-surface-secondary)] rounded font-mono text-xs">
            <span class="text-primary-600 font-bold">DELETE FROM</span> tabelle <span class="text-primary-600 font-bold">WHERE</span> bedingung;
          </div>
          <div class="p-2 bg-[var(--color-surface-secondary)] rounded font-mono text-xs">
            <span class="text-primary-600 font-bold">SELECT</span> a.* <span class="text-primary-600 font-bold">FROM</span> a <span class="text-primary-600 font-bold">JOIN</span> b <span class="text-primary-600 font-bold">ON</span> a.id = b.a_id;
          </div>
          <div class="p-2 bg-[var(--color-surface-secondary)] rounded font-mono text-xs">
            <span class="text-primary-600 font-bold">SELECT</span> COUNT(*), AVG(x) <span class="text-primary-600 font-bold">FROM</span> t <span class="text-primary-600 font-bold">GROUP BY</span> y <span class="text-primary-600 font-bold">HAVING</span> COUNT(*) > 1;
          </div>
        </div>
      </div>

      <!-- CIA Triade -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
        <div class="text-sm font-bold text-primary-600 mb-3">CIA-Triade</div>
        <div class="space-y-2 text-sm">
          <div class="p-2 bg-red-50 border border-red-200 rounded"><strong class="text-red-700">C</strong>onfidentiality (Vertraulichkeit) - Daten nur fuer Berechtigte</div>
          <div class="p-2 bg-yellow-50 border border-yellow-200 rounded"><strong class="text-yellow-700">I</strong>ntegrity (Integritaet) - Daten unveraendert/korrekt</div>
          <div class="p-2 bg-green-50 border border-green-200 rounded"><strong class="text-green-700">A</strong>vailability (Verfuegbarkeit) - System erreichbar</div>
        </div>
      </div>

      <!-- Bezugskalkulation -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
        <div class="text-sm font-bold text-primary-600 mb-3">Bezugskalkulation</div>
        <div class="space-y-1 text-sm font-mono">
          <div class="text-[var(--color-text-primary)]">Listenpreis</div>
          <div class="text-red-500">- Rabatt</div>
          <div class="text-[var(--color-text-primary)] font-bold border-t border-[var(--color-border)] pt-1">= Zieleinkaufspreis</div>
          <div class="text-red-500">- Skonto</div>
          <div class="text-[var(--color-text-primary)] font-bold border-t border-[var(--color-border)] pt-1">= Bareinkaufspreis</div>
          <div class="text-green-500">+ Bezugskosten</div>
          <div class="text-[var(--color-text-primary)] font-bold border-t-2 border-primary-500 pt-1">= Bezugspreis</div>
        </div>
      </div>

      <!-- Stromkosten -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
        <div class="text-sm font-bold text-primary-600 mb-3">Stromkosten</div>
        <div class="p-3 bg-[var(--color-surface-secondary)] rounded text-sm font-mono text-center">
          <div>kWh = (Watt x Stunden x Tage) / 1000</div>
          <div class="mt-2 font-bold text-primary-600">Kosten = kWh x Preis/kWh</div>
        </div>
      </div>

      <!-- IPv6 -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
        <div class="text-sm font-bold text-primary-600 mb-3">IPv6-Adresstypen</div>
        <div class="space-y-2 text-sm">
          <div class="p-2 bg-[var(--color-surface-secondary)] rounded"><strong>Link-Local:</strong> fe80::/10 - Nur im lokalen Netz</div>
          <div class="p-2 bg-[var(--color-surface-secondary)] rounded"><strong>Global Unicast:</strong> 2000::/3 - Weltweit routbar</div>
          <div class="p-2 bg-[var(--color-surface-secondary)] rounded"><strong>Unique Local:</strong> fc00::/7 - Privat (wie RFC1918)</div>
          <div class="p-2 bg-[var(--color-surface-secondary)] rounded"><strong>Multicast:</strong> ff00::/8 - Gruppenadressierung</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const osiLayers = [
  { nr: 7, name: 'Application', examples: 'HTTP, FTP, SMTP, DNS, SSH' },
  { nr: 6, name: 'Presentation', examples: 'TLS/SSL, Kompression, MIME' },
  { nr: 5, name: 'Session', examples: 'NetBIOS, PPTP, RPC' },
  { nr: 4, name: 'Transport', examples: 'TCP, UDP, SCTP' },
  { nr: 3, name: 'Network', examples: 'IP, ICMP, Router, OSPF' },
  { nr: 2, name: 'Data Link', examples: 'Switch, MAC, Ethernet, ARP' },
  { nr: 1, name: 'Physical', examples: 'Kabel, Hub, Repeater, RJ-45' },
]

const subnetTable = [
  { cidr: 8, mask: '255.0.0.0', hosts: '16.777.214' },
  { cidr: 16, mask: '255.255.0.0', hosts: '65.534' },
  { cidr: 20, mask: '255.255.240.0', hosts: '4.094' },
  { cidr: 24, mask: '255.255.255.0', hosts: '254' },
  { cidr: 25, mask: '255.255.255.128', hosts: '126' },
  { cidr: 26, mask: '255.255.255.192', hosts: '62' },
  { cidr: 27, mask: '255.255.255.224', hosts: '30' },
  { cidr: 28, mask: '255.255.255.240', hosts: '14' },
  { cidr: 29, mask: '255.255.255.248', hosts: '6' },
  { cidr: 30, mask: '255.255.255.252', hosts: '2' },
]
</script>
