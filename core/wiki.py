import wikipedia


def fetch_wikipediapedia_data(title):
    """Fetch data from wikipediapedia based on title."""
    try:
        page = wikipedia.page(title)
        return {
            'wikipedia_title': page.title,
            'wikipedia_url': page.url,
            'wikipedia_summary': page.summary,
        }
    except wikipedia.DisambiguationError as e:
        print(f"Disambiguation error: {e.options}")
        return None
    except wikipedia.PageError:
        print(f"No wikipediapedia page found for {title}")
        return None


def search_wikipediapedia_for_lat_lng(lat: float, lng: float):
    """Search wikipediapedia based on user-input latitude and longitude."""
    # Search wikipediapedia using the coordinates
    results = wikipedia.geosearch(lat, lng)

    if not results:
        print("No results found on wikipediapedia for the given coordinates.")
        return

    print("\nFound the following matches on wikipediapedia:")
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
            data = fetch_wikipediapedia_data(chosen_title)
            if data:
                print("\nDetails of the chosen location:")
                print(f"Title: {data['wikipedia_title']}")
                print(f"URL: {data['wikipedia_url']}")
                print(f"Summary: {data['wikipedia_summary']}")
            return
        else:
            print("Invalid choice. Please try again.")
