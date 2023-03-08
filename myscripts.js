
		// Recupera il campo di input
		const input = document.querySelector('#number-input');

		// Aggiunge un ascoltatore di eventi all'input
		input.addEventListener('input', formatNumber);

		function formatNumber(e) {
			// Rimuove tutti gli spazi dal valore dell'input
			const inputValue = e.target.value.replace(/\s/g, '');

			// Aggiunge uno spazio ogni 3 cifre
			const formattedValue = inputValue.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

			// Aggiorna il valore dell'input con la versione formattata
			e.target.value = formattedValue;
		}
