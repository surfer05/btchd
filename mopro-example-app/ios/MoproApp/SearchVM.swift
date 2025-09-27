import MapKit
import Combine

final class SearchVM: NSObject, ObservableObject, MKLocalSearchCompleterDelegate {
    @Published var query: String = ""
    @Published var suggestions: [MKLocalSearchCompletion] = []

    private let completer = MKLocalSearchCompleter()
    private var bag = Set<AnyCancellable>()

    override init() {
        super.init()
        completer.delegate = self
        // Update completer as the user types
        $query
            .debounce(for: .milliseconds(200), scheduler: DispatchQueue.main)
            .sink { [weak self] in self?.completer.queryFragment = $0 }
            .store(in: &bag)
    }

    func completerDidUpdateResults(_ completer: MKLocalSearchCompleter) {
        suggestions = completer.results
    }

    func completer(_ completer: MKLocalSearchCompleter, didFailWithError error: Error) {
        suggestions = []
        print("Search error:", error.localizedDescription)
    }

    /// Resolve a picked suggestion to a coordinate.
    func resolve(_ completion: MKLocalSearchCompletion, then: @escaping (CLLocationCoordinate2D) -> Void) {
        let req = MKLocalSearch.Request(completion: completion)
        MKLocalSearch(request: req).start { resp, _ in
            guard let item = resp?.mapItems.first, let coord = item.placemark.location?.coordinate else { return }
            then(coord)
        }
    }
}
