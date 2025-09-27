import CoreLocation
import SwiftUI

struct ReviewSheet: View {
    var target: CLLocationCoordinate2D
    var onSubmit: (_ categories: [String], _ rating: Int, _ text: String) -> Void
    @Environment(\.dismiss) private var dismiss

    @State private var picks: Set<String> = []
    @State private var rating: Int = 4
    @State private var text: String = ""

    private let cats = [
        "residential", "office", "party", "tourist", "recreational", "unsafe", "commercial",
        "green",
    ]

    var body: some View {
        NavigationStack {
            Form {
                Section("Categories") {
                    ForEach(cats, id: \.self) { c in
                        Toggle(
                            c.capitalized,
                            isOn: Binding(
                                get: { picks.contains(c) },
                                set: { newValue in
                                    if newValue {
                                        picks.insert(c)
                                    } else {
                                        picks.remove(c)
                                    }
                                }
                            ))
                    }
                }
                Section("Rating") {
                    Stepper("Rating: \(rating)", value: $rating, in: 1...5)
                }
                Section("Notes") {
                    TextField("What did you observe?", text: $text, axis: .vertical)
                        .lineLimit(3...6)
                }
                Section {
                    Button("Submit") {
                        onSubmit(
                            Array(picks), rating,
                            text.trimmingCharacters(in: .whitespacesAndNewlines))
                        dismiss()
                    }.disabled(
                        picks.isEmpty
                            || text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
            .navigationTitle("Add a review")
        }
    }
}
