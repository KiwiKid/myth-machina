import wikipedia


def fetch_wikipedia_data(title):
    """Fetch data from Wikipedia based on title."""
    try:
        page = wikipedia.page(title)
        return {
            'wiki_title': page.title,
            'wiki_url': page.url,
            'wiki_summary': page.summary,
        }
    except wikipedia.DisambiguationError as e:
        print(f"Disambiguation error: {e.options}")
        return None
    except wikipedia.PageError:
        print(f"No Wikipedia page found for {title}")
        return None


def search_wikipedia_for_lat_lng(lat: float, lng: float):
    """Search Wikipedia based on user-input latitude and longitude."""
    # Search Wikipedia using the coordinates
    results = wikipedia.geosearch(lat, lng)

    if not results:
        print("No results found on Wikipedia for the given coordinates.")
        return

    print("\nFound the following matches on Wikipedia:")
    for idx, result in enumerate(results, 1):
        print(f"{idx}. {result}")

    # Let the user choose a result
    while True:
        choice = input(
            "\nEnter the number of your choice (or 'exit' to stop): ")
        if choice == 'exit':
            return
        elif choice.isdigit() and 0 < int(choice) <= len(results):
            chosen_title = results[int(choice) - 1]
            data = fetch_wikipedia_data(chosen_title)
            if data:
                print("\nDetails of the chosen location:")
                print(f"Title: {data['wiki_title']}")
                print(f"URL: {data['wiki_url']}")
                print(f"Summary: {data['wiki_summary']}")
            return
        else:
            print("Invalid choice. Please try again.")
