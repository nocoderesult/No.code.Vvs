# Cercetare: DM automat la comentariul „INESS” (IG + TikTok)

Tichet: [issues/03-dm-automat.md](../issues/03-dm-automat.md) · Verificat live pe 21.10.2026 · Surse primare, cu excepțiile marcate „(secundar)”.

## Pe scurt

- **Instagram: se poate.** Meta permite oficial un „private reply”, adică un DM trimis cuiva care ți-a comentat la postare sau reel. Orice unealtă de mai jos face asta. [Meta, Private Replies](https://developers.facebook.com/docs/instagram-platform/private-replies)
- **TikTok, din România: nu se poate, cu nicio unealtă.** API-ul de mesaje TikTok nu e disponibil pentru conturile înregistrate în SEE, Elveția și Marea Britanie. Regula ține de locul în care a fost creat contul. [TikTok, Access to Business Messaging API](https://business-api.tiktok.com/portal/docs/access-to-business-messaging-api/v1.3) Din același motiv, ManyChat blochează explicit TikTok în UE: „Users located in the EU and UK are currently unable to connect their TikTok accounts to Manychat… no estimated timeline”. [ManyChat Help, How to connect TikTok](https://help.manychat.com/hc/en-us/articles/17928990909084-How-to-connect-TikTok-to-Manychat)
- **Nici în afara UE, comentariul nu pornește DM-ul pe TikTok în ManyChat.** În noiembrie 2025, ManyChat spunea că trigger-ul pe comentariu e „still in development” și că e lansat parțial doar în Vietnam, Thailanda și Indonezia. [ManyChat Community, nov. 2025](https://community.manychat.com/manychat-x-tiktok-community-66/new-us-update-7804) Până în aprilie 2026, firul oficial nu arăta nicio lansare. [ManyChat Community, fir 6480](https://community.manychat.com/general-q-a-43/tiktok-auto-dm-from-comments-6480)
- **Concluzie:** pe IG folosim „comentează INESS” → DM automat. Pe TikTok folosim „scrie-mi INESS în mesaj”, cu răspuns automat nativ dacă e disponibil, sau un comentariu fixat (pinned) și link în bio.

## Tabel comparativ

| Unealtă | Instagram | TikTok (cont RO) | Cel mai ieftin plan | Cont cerut | Limite |
|---|---|---|---|---|---|
| **ManyChat** | Da, cu trigger pe comentarii la postări și reels ([help](https://help.manychat.com/hc/en-us/articles/14281316989724-Instagram-Post-and-Reel-Comments-trigger)) | **Nu** (blocat în UE/UK, cere TikTok Business) ([help](https://help.manychat.com/hc/en-us/articles/17928990909084-How-to-connect-TikTok-to-Manychat)) | Free: 0 $. Essential: **14 $/lună la plata anuală** (168 $/an), cu 14 zile de probă ([pricing](https://manychat.com/pricing)). La plata lunară: 17 $ (secundar, [CreatorFlow](https://creatorflow.so/blog/tiktok-comment-to-dm/)) | IG profesional (Creator sau Business). Varianta „Connect via Instagram” **nu cere Pagină de Facebook**, dar are unele funcții limitate ([help](https://help.manychat.com/hc/en-us/articles/14281290924444-How-to-connect-Instagram-to-Manychat)) | Free: **25 contacte active/lună**, 4 automatizări active, mesajul „Powered by Manychat”. Essential: 250 de contacte incluse, apoi 0,10 $ pe contact (lunar) ([pricing](https://manychat.com/pricing)) |
| **CreatorFlow** | Da (Meta Tech Provider, API oficial) ([site](https://creatorflow.so)) | Nu. Spune singur că comment-to-DM pe TikTok „nu există” ([blog](https://creatorflow.so/blog/tiktok-comment-to-dm/)) | Free: 0 $, **500 DM/lună**. Pro: 12 $/lună la plata anuală (15 $ lunar) ([pricing](https://creatorflow.so/pricing)) | IG Business sau Creator ([site](https://creatorflow.so)) | Pro: 5.000 DM/lună |
| **LinkDM** | Da | Nu (doar Instagram) ([pricing](https://linkdm.com/pricing)) | Free: 0 $, **1 cont IG, 1.000 DM/lună**. Pro: 19 $/lună ([pricing](https://linkdm.com/pricing)) | IG Creator sau Business **legat de o Pagină FB** (secundar: [Mavely](https://help.joinmavely.com/knowledge-base/linkdm); help-ul LinkDM trimite la „Attach an Instagram Account to a Facebook Page” ([help](https://www.linkdm.com/help/instagram-connection-error))) | Pro: 25.000 DM/lună |
| **Inrō** | Da („on Instagram”) | Nu e menționat | Free: 0 €, **100 contacte active/lună**, 3 automatizări. Pro: de la 12,99 €/lună, plătești după contactele activate ([pricing](https://www.inro.social/pricing)) | IG profesional (cerință generală Meta) | Free: 3 campanii/lună |
| **TikTok nativ** (Business Suite → Message Center) | – | Doar răspuns automat la **mesaje în DM**, nu la comentarii | Gratuit | Doar conturi cu **Advanced Access** sau **Verified Business Account**. „Receive messages from Everyone” trebuie să fie pornit ([TikTok Help](https://ads.tiktok.com/help/article/how-to-set-up-auto-messages-for-business-accounts?lang=en)) | Cuvânt-cheie de max. 40 de caractere, potrivire exactă. Răspuns de max. 500 de caractere. Mesaj de bun venit de max. 250. Aprobare în 1–5 zile lucrătoare ([TikTok Help](https://ads.tiktok.com/help/article/how-to-set-up-auto-messages-for-business-accounts?lang=en)). Pagina nu spune nimic despre restricții pe regiuni, deci trebuie verificat în aplicație. |

## Regulile platformelor

### Meta (Instagram)
- **Contul:** trebuie să fie profesional (Business sau Creator). Cu „Instagram Login” nu e nevoie de Pagină de Facebook. Cu „Facebook Login” e obligatorie. [Meta, Instagram Platform Overview](https://developers.facebook.com/docs/instagram-platform/overview)
- **Private reply din comentariu:** DM-ul se poate trimite în maximum **7 zile** de la comentariu. Se trimite **un singur mesaj** per comentariu. Ajunge în Inbox dacă persoana te urmărește și în **Requests** dacă nu te urmărește. Mesajele următoare se pot trimite doar dacă persoana răspunde, și doar în 24 de ore de la răspunsul ei. [Meta, Private Replies](https://developers.facebook.com/docs/instagram-platform/private-replies)
- **Fereastra standard de mesaje:** **24 de ore** de la mesajul utilizatorului. Fereastra e de 7 zile doar la reclamele Click-to-Direct. Există și eticheta „Human Agent”, tot de 7 zile, dar e doar pentru răspunsuri scrise de un om. [Meta, Messaging API](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api)
- **Limite de volum:** **750 de private replies pe oră** per cont, la postări și reels. Send API: 100 de apeluri pe secundă pentru text și linkuri. [Meta, Rate Limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting)
- **Dezvăluirea botului:** acolo unde legea o cere, botul trebuie să spună că e automat la începutul conversației. Meta o recomandă și unde nu e obligatoriu. [Meta, Messaging API](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api) La noi se potrivește cu regula „AI info” din hartă.
- **Setarea din aplicație:** „Allow access to messages” trebuie să fie pornit în Message controls. [ManyChat Help, troubleshooting](https://help.manychat.com/hc/en-us/articles/14281291094428-Can-t-connect-Instagram-to-Manychat)

### TikTok
- **API de mesaje:** nu e disponibil pentru conturile din SEE, Elveția și UK. Regiunea se stabilește după locul în care s-a creat contul. Apelurile eșuează chiar dacă autorizarea reușește. [TikTok, Access to Business Messaging API](https://business-api.tiktok.com/portal/docs/access-to-business-messaging-api/v1.3)
- **Conturi eligibile:** API-ul acceptă doar conturi cu Advanced Access sau Verified Business Account (VBA). [TikTok, Business Messaging API](https://business-api.tiktok.com/portal/docs/business-messaging-api/v1.3)
- **Endpoint „Comment-to-Message”:** în API există un endpoint pentru „Comment-to-Message”, dar documentația publică nu se încarcă fără JS și n-am putut confirma ce face exact. Oricum, nu e disponibil în SEE (vezi primul punct). [TikTok, Business Messaging API reference](https://business-api.tiktok.com/portal/docs/business-messaging/v1.3)
- **Fereastra de mesaje (secundar):** 48 de ore de la ultimul mesaj al utilizatorului, cu maximum 10 mesaje din partea ta. Afacerea nu poate începe conversația. [CreatorFlow](https://creatorflow.so/blog/tiktok-comment-to-dm/)
- **Unelte neoficiale:** extensiile de browser sau login-urile cu parolă care „trimit DM la comentarii” intră sub interdicția de automatizare neautorizată din Community Guidelines (secundar, [CreatorFlow](https://creatorflow.so/blog/tiktok-comment-to-dm/)). Le evităm, la fel ca regula „parolele nu se dau”.

## Recomandare

**Instagram: ManyChat.** Pornim pe Free, ca să testăm, și trecem pe **Essential (14 $/lună la plata anuală)** din prima săptămână de postări. Motivele:
1. Se conectează cu Instagram Login, deci nu cere Pagină de Facebook.
2. Are trigger nativ pe comentarii la postări și reels, cu cuvânt-cheie.
3. Costul încape lejer în bugetul de 150–300 €.
4. Dacă TikTok se deschide în UE, se adaugă fără cost suplimentar. ManyChat confirmă „no additional fees” pentru TikTok ([help](https://help.manychat.com/hc/en-us/articles/17928990909084-How-to-connect-TikTok-to-Manychat)).

De ce nu rămânem pe Free: limita de 25 de contacte active pe lună se atinge cu un singur reel care merge bine, iar Free afișează și „Powered by Manychat”.
Variantă cu cost 0: **CreatorFlow Free** (500 DM/lună, fără Pagină FB). Îl folosim dacă vrem să nu plătim nimic în noiembrie.

**TikTok: nu există comment → DM pentru @inessofficial.** Facem așa:
- CTA-ul diferă pe platforme. Pe IG: „Comentează INESS”. Pe TikTok: „Scrie-mi INESS în mesaj”, plus un comentariu fixat (pinned) și link în bio.
- Încercăm răspunsul automat nativ la cuvântul „INESS” (keyword reply). Merge doar dacă contul primește Advanced Access sau VBA.
- Până atunci, răspundem manual la DM-uri o dată pe zi.
- Ne înscriem pe waitlist-ul ManyChat pentru TikTok în UE.

## Pași de configurare

### Instagram + ManyChat (~30–60 min, estimare proprie)
1. În aplicația Instagram, treci contul pe **Creator**: Settings → Account type and tools.
2. Pornește **Allow access to messages** din Settings → Messages → Message controls.
3. Creează contul ManyChat (cere login cu Facebook sau Google). La conectare, alege **Connect via Instagram** ([help](https://help.manychat.com/hc/en-us/articles/14281290924444-How-to-connect-Instagram-to-Manychat)). Parola o introduce doar omul, nu se trimite în chat.
4. Creează o automatizare nouă cu trigger-ul **Instagram Post or Reel Comments** și setările:
   - „Any post”;
   - cuvântul-cheie `INESS`, cu variantele `iness` și `Iness`;
   - opțional, un răspuns public automat la comentariu ([help](https://help.manychat.com/hc/en-us/articles/14281316989724-Instagram-Post-and-Reel-Comments-trigger)).
5. Scrie mesajul DM, care trebuie să încapă într-un **singur mesaj**:
   - dezvăluirea, de exemplu „Sunt asistentul automat al lui Iness”;
   - promisiunea (linkul sau resursa);
   - o întrebare, ca utilizatorul să răspundă și să se deschidă fereastra de 24 de ore.
6. Testează de pe un cont secundar care **nu** urmărește @inessofficial. Mesajul trebuie să apară în Requests.
7. Treci pe Essential (14 zile de probă) înainte de 2 noiembrie.

### TikTok nativ (~15 min de lucru + 1–5 zile lucrătoare de aprobare)
1. Treci contul pe **Business Account** ([TikTok Help](https://ads.tiktok.com/help/article/switch-to-tiktok-business-account)). Leagă-l de un cont TikTok for Business, ca să încerci să obții Advanced Access.
2. Pornește Settings and privacy → Privacy → Direct messages → **Everyone**.
3. Mergi în Profile → ☰ → **Business Suite** → **Message Center** → Automatic messages. Setează:
   - **Keyword reply**: cuvântul `INESS`, răspuns de max. 500 de caractere;
   - **Welcome message**: max. 250 de caractere.
4. Trimite la aprobare **până pe 26 octombrie**, pentru că aprobarea durează 1–5 zile lucrătoare.
5. Dacă opțiunea lipsește, contul nu e eligibil. Rămânem pe varianta manuală și pe link în bio.

## Necunoscute

- Prețul lunar oficial ManyChat Essential, fără plata anuală. Pagina citită arată doar prețul anual, iar cifra de 17 $ e dintr-o sursă secundară.
- Dacă un cont TikTok din România primește Advanced Access și Message Center. Pagina de help nu spune nimic despre regiuni. Se verifică în aplicație.
- Ce face exact endpoint-ul TikTok „Comment-to-Message”. Documentația nu s-a putut citi.
